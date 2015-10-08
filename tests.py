import shade
import sys
import os


class DHCTest:
    # Set some variables
    def __init__(self, username, password, auth_url, project):
        self.auth_username = username
        self.auth_password = password
        self.auth_url = auth_url
        self.project_name = project
        self.region_name = 'RegionOne'
        self.instance_name = 'shadetestinst'
        self.security_group_name = 'shadetestgroup'
        self.volume_name = "testvolume"

    def test_all(self):
        self.connect()

        images = self.list_images()
        flavors = self.list_flavors()

        image = self.get_image(images[0]['id'])
        flavor = self.get_flavor(flavors[0]['id'])

        sec_group = self.create_security_group()
        self.list_security_groups()

        instance = self.launch_instance(image, flavor, self.instance_name, sec_group)
        self.list_servers()

        #volume = self.create_volume()
        #self.attach_volume_to_instance(instance, volume)
        #self.detach_volume_from_instance(instance, volume)
        #self.destroy_volume(volume)

        unused_ip = self.get_ip()
        self.attach_ip_to_instance(instance, unused_ip)
        self.detach_ip_from_instance(instance, unused_ip)

        self.delete_instance(instance)

        self.delete_security_group(sec_group)

    def connect(self):
        print("Connecting to " + self.auth_url)
        self.conn = shade.openstack_cloud(auth_url=self.auth_url,
                username=self.auth_username, password=self.auth_password,
                project_name=self.project_name, region_name=self.region_name)

    # Get a list of images
    def list_images(self):
        print("Getting a list of images")
        images = self.conn.list_images()

        for image in images:
            print(image)

        return images

    # Get a list of flavors
    def list_flavors(self):
        print("Getting a list of flavors")
        flavors = self.conn.list_flavors()

        for flavor in flavors:
            print(flavor)

        return flavors

    # Get a list of servers
    def list_servers(self):
        print("Getting a list of servers")
        servers = self.conn.list_servers()

        for server in servers:
            print(server)

        return servers

    # Get a list of security groups
    def list_security_groups(self):
        print("Getting a list of security groups")
        groups = self.conn.list_security_groups()

        for group in groups:
            print(group)

        return groups

    # Get the image with the id passed in as an argument
    def get_image(self, image_id):
        print("Getting image with id " + image_id)
        image = self.conn.get_image(image_id)
        return image

    # Get the flavor with the id passed in as an argument
    def get_flavor(self, flavor_id):
        print("Getting flavor with id " + flavor_id)
        flavor = self.conn.get_flavor(flavor_id)
        return flavor

    # Launch an instance
    def launch_instance(self, image, flavor, name, security_group):
        print("Launching instance")
        instance = self.conn.create_server(wait=True, auto_ip=False,
            name=name,
            image=image['id'],
            flavor=flavor['id'],
            security_groups=[security_group['name']])

        return instance

    # Create a security group
    def create_security_group(self):
        print("Creating a security group")
        sec_group = self.conn.create_security_group(self.security_group_name, 'for services that run on a worker node')

        print("Creating a security group rule for TCP port 22")
        if not self.conn.create_security_group_rule(sec_group['name'], 22, 22,
                'TCP'):
            print("Failed to create the security group rule")
            sys.exit(1)

        return sec_group

    # Get an unused floating ip
    def get_ip(self):
        print("Getting an unused floating ip")
        unused_floating_ip = self.conn.available_floating_ip()
        return unused_floating_ip

    # Attach an ip to an instance
    def attach_ip_to_instance(self, instance, ip):
        print("Attaching ip to server")
        self.conn.attach_ip_to_server(instance['id'], ip['id'])

    # Detach an ip from an instance
    def detach_ip_from_instance(self, instance, ip):
        print("Detaching ip from server")
        if not self.conn.detach_ip_from_server(instance['id'], ip['id']):
            print("Failed to detach ip from server")
            sys.exit(1)

    # Create a volume that is 1GB
    def create_volume(self):
        print("Creating 1GB volume with name " + self.volume_name)
        vol = self.conn.create_volume(size=1, display_name=self.volume_name)
        return vol

    # Attach a volume to an instance
    def attach_volume_to_instance(self, instance, volume):
        print("Attaching volume to instance")
        self.conn.attach_volume(instance, volume, device='/dev/sdb')

    # Detach a volume from an instance
    def detach_volume_from_instance(self, instance, volume):
        print("Detaching volume from instance")
        self.conn.detach_volume(instance, volume)

    # Delete a volume
    def delete_volume(self, volume):
        print("Deleting volume")
        self.conn.delete_volume(volume['id'])

    # Delete an instance
    def delete_instance(self, instance):
        print("Deleting instance")
        self.conn.delete_server(instance['id'], wait=True)

    # Delete a security group
    def delete_security_group(self, security_group):
        print("Deleting security group")
        if not self.conn.delete_security_group(security_group['id']):
            print("Failed to delete security group")
            sys.exit(1)

# Grab auth info from environment variables
env = os.environ

username = env['OS_USERNAME']
password = env['OS_PASSWORD']
auth_url = env['OS_AUTH_URL']
project = env['OS_TENANT_NAME']

# many auth_urls include the version. this will strip the version
# declaration from the auth_url
if 'v2.0' in auth_url:
    auth_url = '/'.join(auth_url.split('/v2.0')[:-1])

test = DHCTest(username, password, auth_url, project)
test.test_all()
