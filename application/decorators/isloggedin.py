import functools
from flask import redirect, request, g, current_app
from itsdangerous import URLSafeSerializer
cSerializer = URLSafeSerializer('LqR@5DCLIn@RcY$Axj^h5&xXsr4Db324VOT4lh@clb17$1o9J1n!mp$SruRWg$A!')

def isloggedin(f):
    """Check if user is signed in or not."""
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        signin_status = request.cookies.get('interactSignInStatus')
        user_type = request.cookies.get('interactCurrentUser')
        if signin_status and user_type == 'recruiter':
            g.username = request.cookies.get('interactUserName')
            g.useremail = request.cookies.get('interactRecruiterEmail')
            g.userid = request.cookies.get('interactUserIdentification')
            g.work_email = request.cookies.get('interactRecruiterWorkEmail')
            g.contact = request.cookies.get('interactRecruiterContact')
            g.companyname = request.cookies.get('interactCompanyName')
            g.rtype = request.cookies.get('i_rt')
            g.companyid = request.cookies.get('i_ci')
            g.dleft = request.cookies.get('d_li')
            g.lockInteract = request.cookies.get('l_xint_pd')
            g.companylogo = request.cookies.get('i_cll')
            g.paymentid = request.cookies.get('dqw_dxpd')
            g.userimage = request.cookies.get('ulisermg')
            g.preference = request.cookies.get('ipre_men')
            if g.preference is None:
                g.preference = cSerializer.dumps(2)
            if g.companyname == 'None':
                return redirect('/signup/complete')
            return f(*args, **kwargs)
        else:
            return redirect('/signin')
    return wrapped
