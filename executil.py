import logging
logger = logging.getLogger(__name__)
import os
import shlex
import subprocess


def _set_locale(locale):
    env = os.environ.copy()
    env['LC_ALL'] = locale
    return env


def _check_call(cmd, bufsize=0, stdin=None, preexec_fn=None, cwd=None, env=None):
    if not env:
        env = _set_locale('C')

    p = subprocess.Popen(cmd,
                         bufsize=bufsize,
                         stdin=stdin,
                         preexec_fn=preexec_fn,
                         cwd=cwd,
                         env=env)

    returncode = p.wait()
    if returncode != 0:
        raise subprocess.CalledProcessError(returncode, ' '.join(cmd))
    return returncode


def _check_output(cmd, bufsize=0, stdin=None, preexec_fn=None, cwd=None, env=None):
    if not env:
        env = _set_locale('C')

    p = subprocess.Popen(cmd,
                         bufsize=bufsize,
                         stdin=stdin,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         preexec_fn=preexec_fn,
                         cwd=cwd,
                         env=env)

    outdata, errdata = p.communicate()
    if p.returncode != 0:
        raise subprocess.CalledProcessError(p.returncode, ' '.join(cmd), errdata.strip())
    return outdata, errdata


def call(cmd, capture=False, root=None, **kwargs):
    if isinstance(cmd, str):
        cmd = shlex.split(cmd)
    logger.debug('Running %r with capture=%r', ' '.join(cmd), capture)

    if root:
        assert kwargs.get('preexec_fn') is None, 'preexec_fn must be None if using root'
        logger.debug('Changing root to %r', root)
        kwargs['preexec_fn'] = lambda: os.chroot(root)

    if not capture:
        return _check_call(cmd, **kwargs)
    else:
        return _check_output(cmd, **kwargs)
