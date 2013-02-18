from distutils.core import setup
import os


# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir:
    os.chdir(root_dir)

app_name = 'vodkamartiniarticle'
app_name_len = len(app_name) + 1

for dirpath, dirnames, filenames in os.walk(app_name):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        pkg = dirpath.replace(os.path.sep, '.')
        if os.path.altsep:
            pkg = pkg.replace(os.path.altsep, '.')
        packages.append(pkg)
    elif filenames:
        prefix = dirpath[app_name_len:] # Strip "app_name/" or "app_name\"
        for f in filenames:
            data_files.append(os.path.join(prefix, f))

setup(name='vodkamartiniarticle',
      version = __import__(app_name).get_version().replace(' ', '-'),
      description='The fundamental article content type for VodkaMartini',
      author='Alexis Bellido',
      author_email='alexis@ventanazul.com',
      url='https://github.com/alexisbellido/django-vodkamartini-article',
      download_url='https://github.com/alexisbellido/django-vodkamartini-article/tarball/master',
      package_dir={'vodkamartiniarticle': 'vodkamartiniarticle'},
      packages=packages,
      package_data={'vodkamartiniarticle': data_files},

      classifiers=['Development Status :: 3 - Alpha',
                   'Environment :: Web Environment',
                   'Framework :: Django',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Software Development :: Libraries :: Python Modules',
                   'Topic :: Utilities'],
      )
