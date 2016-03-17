Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/trusty64"
  config.vm.network "forwarded_port", guest: 8080, host: 8080
  config.vm.provider "virtualbox" do |vb|
    vb.memory = "4096"
  end

  config.vm.provision "ansible" do |ansible|
    ansible.playbook = "ansible/vagrant_playbook.yml"
    ansible.verbose = "v"
  end
end
