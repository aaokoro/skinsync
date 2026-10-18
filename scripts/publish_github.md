# Publish the public GitHub repo

This environment is not logged into GitHub, so the public remote has to be created on your account.

```bash
# in a browser: github.com/new
# name: skinsync
# public
# do not add a README

git remote add github https://github.com/YOURUSER/skinsync.git
git push -u github cursor/skinsync-final-50e5:main
git push github checkpoint1-frozen-weights
```

Then put that clone URL on the supplemental page and in Overleaf, Recompile, and upload the PDF to Canvas.
