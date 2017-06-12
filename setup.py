from setuptools import setup

setup(
    name='quanthub',
    include_package_data=True,
    version=0.1,
    packages=[
        'quanthub'
    ],
    description='JupyterHub Customization Library',
    author='Knowsis Ltd',
    install_requires=["oauthenticator", "jupyterhub"],
    url="https://github.com/knowsis/jupyterhub_custom"
)
