FROM fedora:22
RUN dnf install -y python python-devel python-pip
RUN adduser peval-user
USER peval-user
RUN mkdir -p ~/git; cd ~/git; git clone https://github.com/GaloisInc/ppaml-eval-tools.git
RUN cd ~/git/ppaml-eval-tools/; pip install --user --ignore-installed .
