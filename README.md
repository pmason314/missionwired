# MissionWired Data Engineer Excercise Documentation

## Initial Setup and Configuration

All code (namely `exercise.py`) was run with a fresh installation of Python 3.10.4, installed via pyenv in a virtual environment created by pyenv-virtualenv.  Any Python version >=3.6 will be able to run `exercise.py`.  VS Code running Windows Subsystems for Linux 2 was the primary IDE.

The only additional package necessary to run the code is `pandas`, though `flake8` and `black` were used during development for linting and formatting respectively.  All packages installed as a result of those three are listed in `requirements.txt`.  The complete list of commands to set up the environment is below:

1. Install pyenv
    * `$ git clone https://github.com/pyenv/pyenv.git ~/.pyenv`
    * `$ echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bash_profile`
    * `$ echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bash_profile `
2. Install pyenv-virtualenv
    * `$ git clone https://github.com/pyenv/pyenv-virtualenv.git $(pyenv root)/plugins/pyenv-virtualenv`
    * `$ echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc`
3. `cd` to the desired working directory
4.  Install Python 3.10.4 and create and activate the virtual environment `mw310`
    * `$ pyenv install 3.10.4`
    * `$ pyenv virtualenv 3.10.4 mw310`
    * `$ pyenv activate mw310`
5. Install packages
    * `$ pip install pandas`
6. (Optional) Install development packages
    * `$ pip install flake8`
    * `$ pip install black`
7. Run `exercise.py`
    * `$ ./exercise.py`

## Reasons for Selected Coding Decisions

### Dropping Extraneous Columns

There are numerous columns across all three tables that are not needed at any point while manipulating and aggregating data.  By removing these at the outset, we save computing time by not copying and merging these unnecessarily.

### Merge Order and Dropping Irrelevant Chapter IDs

The email and subscription tables were merged first to more quickly handle some cases around `chapter_id` and `isunsub`.  Per the instructions we only care about subscription statuses where `chapter_id` is `1` and can further assume all email IDs not present in subscriptions should still be considered subscribed to `chapter_id` `1` , so we first perform an outer left merge to capture all emails with their corresponding `chapter_id` without removing any emails without a listed `chapter_id` at all.  We then replace all null `chapter_id`s from the merge with `1` (per the instruction again) and all corresponding `isunsub` values with `0`.  Finally, we drop all rows where `chapter_id` is not `1` since we explicitly know we don't need them for the `people` table.

### Source Code Selection

Selecting the `code` column for the `people` table was admittedly the most confusing part of this exercise.  Given no context or hint of what this source code should signify or what it might be used for, I opted for a method that would retain as much source information as possible for downstream uses of the `people` table.  We have four different codes from two tables -- both of `create_app` and `create_user` from the constituents and emails table each -- and no apparent relationship between any of them.  I therefore created a 4-tuple of all of those codes (i.e. (email's `create_app`, email's `create_user`, cons's `create_app`, cons's `create_user`)) as the `code` column to maintain all the app and user codes for downstream to decide which are most usesful or valuable.

### Person Created/Updated Selection

Again a little short on context, I made a couple conscious assumptions when choosing both the "Person creation datetime" and "Person updated datetime."  I considered the earliest time a person interacted with the dataset to be their "creation time", namely the earliest/smallest creation date among the constituent, email, and subscription tables.  I alternatively considered just using the created date in the constituent table, but did not find a compelling enough case on either side.

I had a similar logic for the "Person updated datetime," this time categorizing their last interaction with the system in any context to be their last updated.  I created this column by taking the latest/largest datetime among each of the three tables.

### Acquisition Date Selection

Here I used exactly the same logic as I did for the person creation datetime.  This column was simply reused from the `people` table before being casted to a `date` type.