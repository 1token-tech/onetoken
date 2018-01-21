import invoke


@invoke.task
def upload(ctx):
    ctx.run('python setup.py sdist bdist_wheel upload')
    ctx.run('rm -rf build dist ots.egg-info')


@invoke.task
def clean(ctx):
    ctx.run('rm -rf build dist ots.egg-info')
