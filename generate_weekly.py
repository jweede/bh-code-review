import shutil, git, re, pystache
from datetime import date, timedelta

GIT_DIR = "/home/jweede/bh/git-trunk"
template_name = "weekly_review"

nginx_dir = "/usr/share/nginx/www/" # make sure you fix permissions or run as root

rev_re = re.compile(r'\s*git-svn-id:.*@(\d+)\s')

def get_revs_from_git( since_date, git_dir=GIT_DIR):
    g = git.Git(git_dir)
    log_output = g.log("--pretty=full","--since=%s" % since_date)
    #extract revs
    revs = []
    for line in log_output.split('\n'):
        m = rev_re.match(line)
        if m:
            revs.append(m.group(1))
    # print revs
    return { 'raw_log':log_output 
           , 'revs':revs }

def generate_review_page_from_revs( revs_obj, since_date ):
    templ_vals = {'today': date.today().isoformat()
                 ,'since_date': since_date
                 ,'raw_log': revs_obj['raw_log']
                 ,'revs': revs_obj['revs']
                 }
    mustache_name = '%s.html.mustache' % template_name
    output_name = '%s.html' % template_name

    with open(mustache_name,'r') as templatef, open(output_name,'w') as outputf:
        outputf.write( pystache.render(templatef.read(), templ_vals) )

def copy_output_to_nginx():
    shutil.copy('%s.html' % template_name, nginx_dir)

if __name__ == '__main__':
    # We run ours every thursday.
    last_thursday = (date.today() - timedelta(weeks=1)).isoformat()
    revs_obj = get_revs_from_git( last_thursday )
    
    generate_review_page_from_revs( revs_obj, last_thursday )

    copy_output_to_nginx()