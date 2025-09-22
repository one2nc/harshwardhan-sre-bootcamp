# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "generic/debian12"
  config.vm.network "forwarded_port", guest: 8080, host: 8080

  config.vm.synced_folder ".", "/vagrant"
  config.vm.provision "docker"

  config.vm.provision "shell", inline: <<-SHELL
    apt update
    apt install -y docker-compose make python3
    cd /vagrant
    make serve-docker
  SHELL
end
