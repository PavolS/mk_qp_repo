#!/usr/bin/env python3

import sys
import os
import shutil
import traceback

from ruamel.yaml import YAML
yaml=YAML()

GITHUB_WORKFLOWS_PATH=os.path.join(".github", "workflows")
PATHS_KEY = "paths"
IGNORE_PATHS_KEY = "paths-ignore"

def update_paths(paths, repo_name):
    for i, path in enumerate(paths):
        paths[i] = os.path.join(repo_name, path)
    return paths

def update_action(action, repo_name):

    if not PATHS_KEY in action:
        action[PATHS_KEY] = ["**"]
    update_paths(action[PATHS_KEY], repo_name)

    if IGNORE_PATHS_KEY in action:
        update_paths(action[IGNORE_PATHS_KEY], repo_name)

    return action

def update_workflow(workflow, repo_name):
    for action in workflow.get('on', {}).values():
        update_action(action, repo_name)
    return workflow
    
def main(argv):
    location = argv[1]
    repo_names = argv[2:]
    workflows = {}
    others = {}
    target_workflows_dir = os.path.join(location, GITHUB_WORKFLOWS_PATH)

    for repo_name in repo_names:
        source_workflows_dir = os.path.join(location, repo_name, GITHUB_WORKFLOWS_PATH)
        try:
            filenames = os.listdir(source_workflows_dir)
        except:
            traceback.print_exc(10)
            continue
        for filename in filenames:
            filepath = os.path.join(source_workflows_dir, filename)
            if filename[-4:] in { "yaml", ".yml"}:
                workflow = yaml.load(open(filepath))
                workflows[(repo_name, filename)] = update_workflow(workflow, repo_name)
            else:
                if filename in others:
                    raise RuntimeError("Conflicting name for workflow script: '{}'".format(filename))
                others[filename]=filepath

    os.makedirs(target_workflows_dir)

    for (repo_name, filename), data in workflows.items():
        target_stream = open( 
            os.path.join(location, GITHUB_WORKFLOWS_PATH, "{}-{}".format(repo_name, filename)), 
            'w' )
        yaml.dump(data, target_stream)

    for (filename, source_path) in others.items():
        shutil.copyfile(source_path, os.path.join(target_workflows_dir, filename))
    

if __name__ == "__main__":
    main(sys.argv)
    sys.exit(0)