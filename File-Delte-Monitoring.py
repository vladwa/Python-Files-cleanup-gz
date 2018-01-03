'''
@author: vladwa
'''

import logging

import sys
import threading
import traceback
from Queue import Queue
from threading import Thread
from time import sleep
from ConfigProcessor import ConfigProcessor
from FileDeleteJob import FileDeleteJob
from SSH import SSH
import time
jobs_queue = Queue()
jobs_ids_list = []
from datetime import datetime
from pytz import timezone
import pytz

logging.basicConfig(
    format='%(asctime)s:%(thread)d:%(levelname)s:%(message)s',
    level=logging.INFO, filename="File-Delete-Monitoring.log"
)

def get_epoch_time():
    return int(time.time())

def get_pst_time():
    date_format='%m_%d_%Y_%H_%M_%S_%Z'
    date = datetime.now(tz=pytz.utc)
    date = date.astimezone(timezone('US/Pacific'))
    pstDateTime=date.strftime(date_format)
    return pstDateTime

def get_job_details(job):
    job_details = ""
    for attr, value in job.__dict__.iteritems():
        if not attr.startswith("ssh_password"):
            job_details += "%s: %s, " % (str(attr or ""), str(value or ""))
    print "job_details", job_details
    return job_details

def check_list_empty(inputList):
    if not inputList:
        return True
        logging.info("The File to be zipped does not exist , hence not creating tar file!!")
    else:
        return False
        logging.info("The File to be zipped does not exist , hence not creating tar file!!: %s" %(inputList))

def write_log_info(status,outPutMessage):
    if (status == True):
        logging.info("Tar file generated successfully : %s" %(outPutMessage))
    else:
        logging.info("Error while generating Tar File: %s" %(outPutMessage))
    
def worker():
    while True:
        try:
            data = jobs_queue.get()
            print "data",data[0]
            job = data[0]
            ssh = SSH()
            interval = job.interval
            enabled = job.enabled
            ssh_machine = job.ssh_machine.split(',')
            ssh_username = job.ssh_username
            ssh_password = job.ssh_password
            directory = job.directory.split(',')
            sudo = job.sudo
            tar = job.tar
            tar_location=job.tar_location
            status, output, error = None, None, None
            epochTime = get_epoch_time()
            if enabled:
                count = 0
                offsets_queue = []
                job_details = get_job_details(job)
                logging.info("Job[%s]: Starting job... interval=%s, directory=%s, sudo=%s, tar=%s, tarLocation=%s" % (
                jobid, interval, directory,sudo, tar,tar_location))
                while True:
                    for ip in ssh_machine:
                        for file in directory:
                            #command = "/bin/rm -rf %s" %  (file)
                            #logging.info("Executing: %s" % command)
                            tarFileName=file.split('/')[-1]
                            print tarFileName
                            tarLocation=file.rsplit('/',1)[:1][0]
                            pstTime = get_pst_time()
                            tarCommand = "[ -f %s ] && cd  %s && tar -cvzf %s_%s.tar.gz %s --remove-files" %(file,tarLocation,tarFileName,pstTime,tarFileName)
                            logging.info("Tar command executed is: %s" % tarCommand)
                            logging.info("Tar files are stored in the location: %s" %tarLocation)
                            status, output, error = None, None, None
                            try:
                                if sudo:
                                    if tar :
                                        status, output = ssh.run_sudo_command(ssh_username=ssh_username, ssh_password=ssh_password,
                                                                                  ssh_machine=ip, command=tarCommand, jobid=jobid)
                                        logging.info("Tar Command Executed is : %s , output of tar command : %s" % (tarCommand,output))
                                        listStatus=check_list_empty(output)
                                        write_log_info(listStatus, output)
                                    else:
                                        status, output = ssh.run_sudo_command(ssh_username=ssh_username, ssh_password=ssh_password,
                                                                                  ssh_machine=ip, command=command, jobid=jobid)
                                        logging.info("Tar Command Executed is : %s , output of tar command : %s" % (tarCommand,output))
                                        listStatus=check_list_empty(output)
                                        write_log_info(listStatus, output)  
                                else:
                                    if tar:
                                        status, output = ssh.run_command(ssh_username=ssh_username, ssh_password=ssh_password,
                                                                         ssh_machine=ip, command=tarCommand, jobid=jobid,
                                                                         job_details=job_details)
                                        logging.info("Tar Command Executed is : %s , output of tar command : %s" % (tarCommand,output))
                                        listStatus=check_list_empty(output)
                                        write_log_info(listStatus, output)
                                    else:
                                        status, output = ssh.run_command(ssh_username=ssh_username, ssh_password=ssh_password,
                                                                         ssh_machine=ip, command=command, jobid=jobid,
                                                                         job_details=job_details)
                                        listStatus=check_list_empty(output)
                                        write_log_info(listStatus, output)  
                            except ValueError:
                                logging.error("Job[%s]: Could not run command:%s" % (jobid, sys.exc_info()[0]))
                                logging.error(traceback.format_exc())
                                error = str(traceback.format_exc())
                                print error
                                status = False
                            logging.info("Job[%s]: Sleeping for %s secs..." % (jobid, interval))
                    sleep(interval)
            else:
                logging.info("Job[%s]: Is set to disable state." % jobid)
        except:
            #logging.error("Job[%s]: Unexpected error:%s, output:%s" % (jobid, sys.exc_info()[0], output))
            logging.error(traceback.format_exc())
        finally:
            jobs_queue.task_done()

if __name__ == "__main__":
    cp = ConfigProcessor()
    config, sections = cp.get_sections("fileDeleteSetting.cfg")
    jobs = []
    for section in sections:
        env = cp.get_config_section_map(config, section)
        enabled = int(env["enabled"])
        if enabled:
            interval = int(env["interval"])
            ssh_username = env["ssh_username"]
            ssh_password = env["ssh_password"]
            ssh_machine = env["ssh_machine"].split(",")
            environment = env["env"]
            directorys = env["directory"].split(",")
            sudo = int(env["sudo"])
            tar = env["tar"]
            tar_location = env["tar_location"]
            for ssh_machines in ssh_machine:
                for directory in directorys:
                    print directory
                    job = None
                    jobid = "%s-%s" % (environment,ssh_machines)
                    job = FileDeleteJob(jobid=jobid,interval=interval,
                                enabled=enabled,ssh_username=ssh_username, ssh_password=ssh_password,ssh_machine=ssh_machines,
                                environment=environment,directory=directory,sudo=sudo,tar=tar,tar_location=tar_location)
                    jobs.append(job)
                    for attr, value in job.__dict__.iteritems():
                        logging.info("%s: %s" % (str(attr or ""), str(value or "")))
                        # exit()
                    logging.info("Added job(%s) to queue [%s(environment) ==> %s(ssh_machine)]" % (jobid,environment,ssh_machines))
        
    
    logging.info("No of jobs in queue: %s" % len(jobs))
    for job in jobs:
        if job.enabled:
            job_worker = Thread(target=worker, args=())
            job_worker.setDaemon(True)
            job_worker.setName(job.jobid+job.directory)
            job_worker.start()
    
    for job in jobs:
        if job.enabled:
            logging.info("Job[%s]: Enabled" % job.jobid+job.directory)
            jobs_ids_list.append(job.jobid)
            data = [job]
            jobs_queue.put(data)
            sleep(1)
    jobs_queue.join()