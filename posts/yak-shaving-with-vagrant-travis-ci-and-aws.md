<!--
.. title: Yak shaving with Vagrant, Travis-CI and AWS
.. slug: yak-shaving-with-vagrant-travis-ci-and-aws
.. date: 2016/11/18 17:01:00
.. tags:
.. spellcheck_exceptions: Ansible, aws, LoadError, mkmf, LTS, Tldr,devel,dev,libxml,libxslt,sudo,repos,zlib,Homebrew
.. is_orphan: False
.. link:
.. description:
-->

Tldr; Don't use the vagrant package from your distribution if you intent to build plugins.

I've just finished setting up CI pipeline for a personal project. The project has an ansible playbook that I want to exercise every time there's a commit or a PR. While completing the task I [shaved a yak](http://catb.org/jargon/html/Y/yak-shaving.html) and narrowly avoided shaving a whole herd. I planned to use Vagrant in my Travis-CI pipeline to start an instance in AWS, run the playbook, look at the result and terminate the instance. Vagrant, Travis-CI and AWS are pretty common tools, so I was surprised at the wrangling involved before I ended up with a solution. I thought I'd document my findings to minimise the chance that others will have the same experience.

# Finding #1: Travis' default build agent has an old Vagrant

The default build agent is based on Ubuntu 12.04 LTS Server which ships with Ansible 1.0 in its apt repo. The [vagrant-aws](https://github.com/mitchellh/vagrant-aws) plugin requires Vagrant 1.2. Fortunately they have a [Ubuntu 14.04 LTS Server beta](https://docs.travis-ci.com/user/trusty-ci-environment) which has a newer Vagrant in the apt repo.

# Finding #2: The AWS-Vagrant plugin won't build with a newer Vagrant because of missing libraries tools

```
$ vagrant plugin install vagrant-aws
Installing the 'vagrant-aws' plugin. This can take a few minutes...
/usr/lib/ruby/1.9.1/rubygems/installer.rb:562:in `rescue in block in build_extensions': ERROR: Failed to build gem native extension. (Gem::Installer::ExtensionBuildError)

        /usr/bin/ruby1.9.1 extconf.rb
/usr/lib/ruby/1.9.1/rubygems/custom_require.rb:36:in `require': cannot load such file -- mkmf (LoadError)
	from /usr/lib/ruby/1.9.1/rubygems/custom_require.rb:36:in `require'
	from extconf.rb:4:in `<main>'
```

Searching for the mkmf LoadError in the context of Debian and Ubuntu gives recommendations to install a few devel packages including ruby-dev (some will say a specific version of ruby dev). It seems that AWS-Vagrant is a Ruby gem, and gems are built on-box (at least it seems so - I'm a Ruby rookie), so libraries and the ruby compiler are needed. These aren't installed on the build agent.

`$ sudo apt-get install build-essential libxslt-dev libxml2-dev zlib1g-dev ruby-dev`

# Finding #3: The AWS-Vagrant plugin needs Ruby version 2.0+

```
$ vagrant plugin install vagrant-aws
Installing the 'vagrant-aws' plugin. This can take a few minutes...
/usr/lib/ruby/1.9.1/rubygems/installer.rb:388:in `ensure_required_ruby_version_met': json requires Ruby version ~> 2.0. (Gem::InstallError)
	from /usr/lib/ruby/1.9.1/rubygems/installer.rb:156:in `install'
	from /usr/lib/ruby/1.9.1/rubygems/dependency_installer.rb:297:in `block in install'
	from /usr/lib/ruby/1.9.1/rubygems/dependency_installer.rb:270:in `each'
	from /usr/lib/ruby/1.9.1/rubygems/dependency_installer.rb:270:in `each_with_index'
```

`vagrant plugin install` wants to use Ruby 1.9.1 to perform the gem build, but that version is too old. Fortunately the build agent has Ruby 2.3.


# Finding #4: Ubuntu Vagrant can't load plugins built with Ruby 2.3

```
$ gem install --verbose vagrant-aws
...
Successfully installed vagrant-aws-0.7.2
41 gems installed
$ vagrant plugin install /home.travis/.rvm/gems/ruby-2.3.1/cache/vagrant-aws-0.7.2.gem
/usr/lib/ruby/1.9.1/rubygems/format.rb:32:in `from_file_by_path': Cannot load gem at [/home.travis/.rvm/gems/ruby-2.3.1/cache/vagrant-aws-0.7.2.gem] in /home/travis/build/edwinsteele/biblebox-pi (Gem::Exception)
	from /usr/share/vagrant/plugins/commands/plugin/action/install_gem.rb:36:in `call'
	from /usr/lib/ruby/vendor_ruby/vagrant/action/warden.rb:34:in `call'
	from /usr/share/vagrant/plugins/commands/plugin/action/bundler_check.rb:20:in `call'
	from /usr/lib/ruby/vendor_ruby/vagrant/action/warden.rb:34:in `call'
	from /usr/lib/ruby/vendor_ruby/vagrant/action/builder.rb:116:in `call'
...
```

Now I'm running out of ideas and I'm considering less conventional means like building on the Travis MacOS environment where I can use Homebrew or moving to another CI hosting provider entirely. Fortunately I stumbled on the answer...

# The Answer

From https://www.vagrantup.com/docs/installation/

> Beware of system package managers! Some operating system distributions include a vagrant package in their upstream package repos. Please do not install Vagrant in this manner. Typically these packages are missing dependencies or include very outdated versions of Vagrant. If you install via your system's package manager, it is very likely that you will experience issues. Please use the official installers on the downloads page.

Yeah, I experienced issues. Once I followed the advice it was smooth 

```
$ wget -O /tmp/vagrant.deb https://releases.hashicorp.com/vagrant/1.8.7/vagrant_1.8.7_x86_64.deb
$ sudo dpkg -i /tmp/vagrant.deb
$ vagrant plugin install vagrant-aws
$
```

And now I have a CI pipeline running on AWS after each commit. Nice.