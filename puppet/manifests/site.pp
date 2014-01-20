##Make sure all the packages are up to date
exec { "apt-update":
    command => "/usr/bin/apt-get update"
}

Exec["apt-update"] -> Package <| |>

class { 'python':
  version    => '2.7',
  pip        => true,
  dev        => true,
  virtualenv => true
}

Package {ensure => "installed"}
$mypackages = ["libxml2-dev", "libxslt-dev"]
package {$mypackages:}

python::virtualenv { '/home/vagrant/virtenv':
  owner        => 'vagrant',
  group        => 'vagrant',
  cwd          => '/home/vagrant/virtenv',
  distribute   => false,
  timeout      => 10000
}

#Hack to get requirements installed, since the python module doesn't seem to work
exec {"pip_install_requirements":
  command => "/home/vagrant/virtenv/bin/pip install -r /vagrant/requirements.txt"
}
