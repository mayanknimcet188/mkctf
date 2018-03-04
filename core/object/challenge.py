# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     file: challenge.py
#     date: 2018-02-27
#   author: paul.dautry
#  purpose:
#
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# =============================================================================
#  IMPORTS
# =============================================================================
import os
import os.path as path
from stat import S_IRWXU
from subprocess import PIPE, Popen, TimeoutExpired, CalledProcessError
from core.wrapper import lazy
from core.object.configurable import Configurable
# =============================================================================
#  CLASSES
# =============================================================================
##
## @brief      Class for challenge.
##
class Challenge(Configurable):
    ##
    ## @brief      { function_description }
    ##
    ## @param      size       The size
    ##
    @staticmethod
    def make_flag(repo_conf, size=32):
        return "{}{}{}".format(repo_conf['flag']['prefix'],
                               os.urandom(size).hex(),
                               repo_conf['flag']['suffix'])
    ##
    ## @brief      Constructs the object.
    ##
    def __init__(self, logger, chall_conf_path, repo_conf):
        super().__init__(logger, chall_conf_path)
        self.repo_conf = repo_conf
    ##
    ## @brief      Creates a dir.
    ##
    ## @param      directory  The directory
    ##
    def __create_dir(self, directory):
        dir_path = path.join(self.working_dir(), directory)

        if not path.isdir(dir_path):
            os.mkdir(dir_path)

            return True

        return False
    ##
    ## @brief      Creates a dir.
    ##
    ## @param      directory  The directory
    ##
    def __create_file(self, file, executable=False):
        file_path = path.join(self.working_dir(), file)

        os.makedirs(path.dirname(file_path), exist_ok=True)

        if not path.isfile(file_path):
            with open(file_path, 'w') as f:
                if executable:
                    f.write('#!/usr/bin/env bash\n')

                f.write('# file automatically generated by mkctf.\n')

                if executable:
                    f.write('>&2 echo "not implemented."\n')
                    f.write('exit 4\n')

            if executable:
                os.chmod(file_path, S_IRWXU)

            return True

        return False
    ##
    ## @brief      { function_description }
    ##
    def __run(self, args, timeout):
        proc = Popen(args, stdout=PIPE, stderr=PIPE, cwd=self.working_dir())

        try:
            stdout, stderr = proc.communicate(timeout=timeout)
        except TimeoutExpired as e:
            proc.terminate()
            return (None, e.stdout, e.stderr)
        except CalledProcessError as e:
            proc.terminate()
            return (e.returncode, e.stdout, e.stderr)

        return (proc.returncode, stdout, stderr)
    ##
    ## @brief      Returns challenge's category
    ##
    @lazy('__category')
    def category(self):
        return path.split(path.split(self.working_dir())[0])[-1]
    ##
    ## @brief      Returns challenge's slug
    ##
    @lazy('__slug')
    def slug(self):
        return path.split(self.working_dir())[-1]
    ##
    ## @brief      Determines if static.
    ##
    ## @return     True if static, False otherwise.
    ##
    def is_standalone(self):
        return self.get_conf('standalone')
    ##
    ## @brief      Determines if enabled.
    ##
    ## @return     True if enabled, False otherwise.
    ##
    def enabled(self):
        return self.get_conf('enabled')
    ##
    ## @brief      Enables/Disables challenge
    ##
    ## @param      enabled  The enabled
    ##
    def enable(self, enabled):
        conf = self.get_conf()
        conf['enabled'] = enabled
        self.set_conf(conf)
    ##
    ## @brief      { function_description }
    ##
    def renew_flag(self, size):
        conf = self.get_conf()
        conf['flag'] = Challenge.make_flag(self.repo_conf, size)
        self.set_conf(conf)
        return conf['flag']
    ##
    ## @brief      Creates a new challenge
    ##
    ## @param      self  The object
    ## @param      conf  The conf
    ##
    ## @return     { description_of_the_return_value }
    ##
    def create(self):
        try:
            os.makedirs(self.working_dir())
        except:
            return False

        directories = self.repo_conf['directories']['public'][::]
        directories += self.repo_conf['directories']['private']

        for directory in directories:
            if not self.__create_dir(directory):
                self.logger.warning("failed to create directory: "
                                    "{}".format(directory))

        for file in self.repo_conf['files']['txt']:
            if not self.__create_file(file):
                self.logger.warning("failed to create file: "
                                    "{}".format(file))

        bin_files = [
            self.repo_conf['files']['build'],
            self.repo_conf['files']['deploy'],
            self.repo_conf['files']['status']
        ]

        for file in bin_files:
            if not self.__create_file(file, executable=True):
                self.logger.warning("failed to create file: "
                                    "{}".format(file))

        return True
    ##
    ## @brief      Yields files contained in public folders
    ##
    def exportable(self):
        wd = self.working_dir()
        for directory in self.repo_conf['directories']['public']:
            dir_path = path.join(wd, directory)
            for de in self._scandirs(dir_path):
                yield de
    ##
    ## @brief      { function_description }
    ##
    def build(self, timeout=4):
        script = self.repo_conf['files']['build']
        if not '/' in script:
            script = './{}'.format(script)
        return self.__run([script], timeout)
    ##
    ## @brief      { function_description }
    ##
    def deploy(self, timeout=4):
        script = self.repo_conf['files']['deploy']
        if not '/' in script:
            script = './{}'.format(script)
        return self.__run([script], timeout)
    ##
    ## @brief      { function_description }
    ##
    def status(self, timeout=4):
        script = self.repo_conf['files']['status']
        if not '/' in script:
            script = './{}'.format(script)
        return self.__run([script], timeout)


