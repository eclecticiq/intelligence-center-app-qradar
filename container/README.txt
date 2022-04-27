Use the following sub-directories for any dependencies and scripts that your app container needs:

container/pip:
  - Holds Python packages.
  - Packages are installed when the app image is built.
  - Package ordering:
    - Supply an ordering.txt file: causes multiple invocations of pip, in the specified order.
    - Without ordering.txt, all packages in the directory are passed to a single invocation of pip.
  - Using a requirements.txt file to identify Python package dependencies is no longer supported.
  - Calls to pip install use the --no-index flag to ensure that dependencies are not downloaded
    from an external source.

container/rpm:
  - Holds RPM packages.
  - Packages are installed when the app image is built.
  - An ordering.txt file can be supplied to define the order in which the packages are installed.
  - All packages are passed to a single rpm command invocation.
  - rpm is invoked with these options: --replacepkgs --excludedocs.

container/build:
  - Holds other scripts/dependencies that can be handled when the app image is built.
  - You must supply a container/build/ordering.txt file that lists the scripts to be executed.
  - Scripts are executed when the app image is built.

container/run:
  - Holds scripts that can be handled only when the app container is started.
  - You must supply a container/run/ordering.txt file that lists the scripts to be executed.
  - Scripts are executed when the app container is started.

container/clean:
  - Holds cleanup.sh script to be run when the app container is shut down.

container/conf:
  - Holds any configuration files used by the app.

container/conf/supervisord.d:
  - The content of this directory will be copied to /etc/supervisord.d/ in the container
    and will be included as a part of the container's supervisord configuration.

container/service:
  - Holds scripts that start up any background processes used by your app.


In summary:
  During the app image build, the SDK will:
    - install Python packages from container/pip
    - install RPM packages from container/rpm
    - execute scripts listed in container/build/ordering.txt.

  When the app container is started, the SDK will:
    - execute scripts listed in container/run/ordering.txt.
