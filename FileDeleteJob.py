class FileDeleteJob:

    def __init__(self,jobid, interval, enabled,ssh_username,ssh_password, ssh_machine, environment,directory,sudo,tar,tar_location):
        self.jobid = jobid
        self.interval = interval
        self.enabled = enabled
        self.ssh_username = ssh_username
        self.ssh_password = ssh_password
        self.ssh_machine = ssh_machine
        self.environment = environment
        self.directory = directory
        self.sudo = sudo
        self.tar = tar
        self.tar_location = tar_location