import os
import pipes
from subprocess import Popen, PIPE, STDOUT

import grp

import pwd
from jupyterhub.auth import LocalAuthenticator
from oauthenticator import GoogleOAuthenticator
from traitlets import Unicode


class CustomLocalAuthenticator(LocalAuthenticator):
    environment_config_file = Unicode(
        '',
        help="""Path to an environment configuration file that can be used
        to create environments for each user created in the system.             
        """).tag(config=True)

    def add_system_user(self, user):
        """
        Create a new local UNIX user on the system.
        Create default environment for user from the specified environment file
        """
        super().add_system_user(user)

        self.create_default_conda_environment(user)

    def create_default_conda_environment(self, user):

        """
        Create environment for user from the specified environment file
        Append environment to txt file so it appears in jupyter as a kernel
        option
        """

        if self.environment_config_file:

            name = user.name

            cmd = ['su', '-', name, "-c",
                   "/opt/anaconda/bin/conda-env create -f {0} -v "
                   "--force".format(self.environment_config_file, name)
            ]

            self.log.info("Creating user environment from config: %s",
                          ' '.join(map(
                              pipes.quote, cmd)))

            p = Popen(cmd, stdout=PIPE, stderr=STDOUT)

            stdout, stderr = p.communicate()

            if p.returncode:
                err = p.stdout.read().decode('utf8', 'replace')
                raise RuntimeError(
                    "Failed to create user default environment "
                    "{0}: {1}".format(name, err)
                )

            location = '/data/{0}/.conda/envs/local\n'.format(name)

            with open("/data/{0}/.conda/environments.txt".format(name), "a+") \
                    as file:

                for line in file:
                    if line == location:
                        break
                else:  # not found, we are at the eof
                    file.write(location)  # append missing data

            uid = pwd.getpwnam(name).pw_uid
            gid = grp.getgrnam(name).gr_gid

            os.chown("/data/{0}/.conda/environments.txt".format(name), uid, gid)


class CustomGoogleOAuthenticator(
    CustomLocalAuthenticator, GoogleOAuthenticator):
    """A version that mixes in local system user creation"""
    pass
