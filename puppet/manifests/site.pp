##Make sure all the packages are up to date
exec { "apt-update":
    command => "/usr/bin/apt-get update"
}

Exec["apt-update"] -> Package <| |>

class { 'python':
  version    => '2.7',
  dev        => true,
  virtualenv => true
}

Package {ensure => "installed"}
$mypackages = ["libxml2-dev", "libxslt-dev"]
package {$mypackages:}

python::virtualenv { '/home/vagrant/virtenv':
  requirements => '/vagrant/requirements.txt',
  owner        => 'vagrant',
  group        => 'vagrant',
  cwd          => '/home/vagrant/virtenv',
  timeout      => 1000000
}

#python::pip {'scraper': virtualenv => '/home/vagrant/virtenv'}
#
#python::requirements { '/vagrant/requirements.txt':
#  virtualenv => '/home/vagrant/virtenv',
#  owner      => 'vagrant',
#  group      => 'vagrant'
#}
