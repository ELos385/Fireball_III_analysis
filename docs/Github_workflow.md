# Overview of the Workflow
•	Each diagnostic is developed in its own Git branch
•	As much as possible, contributors work only on their branch
•	Contributors do not merge main
•	The repo maintainer reviews code, resolves conflicts, and merges into main

This will minimise the risk of conflicts as we build the repo.

## Table of Contents
- [One-time Setup](##One-time_Setup)
- [Starting Work on a Diagnostic](##Starting_Work_on_a_Diagnostic)
- [Push your branch to GitHub](##Push_your_branch_to_GitHub)
- [Open a Pull Request](##Open_a_Pull_Request)
- [Review and merge (Maintainer only)](##Review_and_merge_(Maintainer_only))


## One-time Setup

Open a terminal and navigate to you SWAN_projects folder. 

Clone the repository:

```bash
git clone https://github.com/ELos385/Fireball_III_analysis.git
cd Fireball_III_analysis
```

Make sure main is up to date:

```bash
git checkout main
git pull origin main
```

## Starting Work on a Diagnostic
Branches for diagnostics should follow this convention:

```bash
diagnostic/<diagnostic_name>
```

To make a branch for your diagnostic and start working there:

```bash
git switch -c diagnostic/my_diagnostic
```

## Making Changes and Committing

•	Initialise your diagnostic in “diagnostics.toml”
•	Implement your diagnostic class (re-use processing scripts from OLD FB3 repo if possible)
•	Set up the calibration files
•	Keep changes scoped to your diagnostic where possible

Commit your changes (do this often :))

```bash
git status
git add path/to/changed_files.py
git commit -m "Add MyDiagnostic class"
```

You can always commit locally, and you do not need to pull before committing.

## Push your branch to GitHub

When your diagnostic is ready to be merged with main, push using:

```bash
git push -u origin diagnostic/my_diagnostic
```

After the first push, you can use:

```bash
git push
```

If you see an error when pushing, GitHub likely has new commits. Run:

```bash
git pull
git push
```

If Git reports conflicts, stop and contact the maintainer. Do not attempt to resolve conflicts with main yourself unless explicitly asked.

## Open a Pull Request

•	Go to GitHub
•	Open a Pull Request
o	Base branch: main
o	Compare branch: diagnostic/<your_diagnostic>
•	In the description, briefly explain which changes you made

Do not merge your own Pull Request.

## Review and merge (Maintainer only)
•	Review the code, request changes if needed and merge with main.
