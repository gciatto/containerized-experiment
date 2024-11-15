## What is this repository?

Didactical repository exemplifying how a Jupyter notebook can be converted into a script, 
and its execution can be automated via Docker and Docker Compose.

This is part of the PhD course __"Containerisation and Orchestration for Research Reproducibility"__ 
held by me at the University of Bologna.

## Pay attention to the history of commits

Run: `git log --oneline` to inspect the history of commits:

```plaintext
19ba9fe (HEAD -> master, origin/master) feat: split experiments into different services
8293534 feat: support gridcv models parametrization
0fc62ff feat: organize experimental results to avoid repetitions
9e78fce fix: persmissions on data folder
9345702 feat: dockerize
84d3822 feat!: transform notebook into script
078562f feat: experiments notebook
```

1. Initially (`19ba9fe`), the repository contained a Jupyter notebook with experiments
2. The first step (`84d3822`) was to convert the notebook into a script
3. The second step (`9345702`) was to dockerize the script (adding a `Dockefile` and a `docker-compose.yml`)
4. To avoid issues with file permissions on the host, further changes (`9e78fce`) were made to the `Dockefile`
5. The script was further improved (`0fc62ff`) to let the script recognize if a given experiment was already executed
6. The script was further improved (`8293534`) to allow for running scripts in parallel with different parameters

> Use `git checkout <COMMIT_HASH>` to inspect the repository at a given commit

## Further possible improvements

+ Use GHA to automate the build of the Docker image
+ Use GHA to automate the execution of the experiments
+ Use Renovate or Dependabot to keep the dependencies up-to-date

## Exercise / Exam

1. Select some experiment of your choice from your own (or your group's) research activity
    + better if it is from an already published paper
    + better if it is a Jupyter notebook

2. Dockerize the solution in such a way that:
    + only scripts are present (no notebooks)
    + the experiments are dockerized and can be run via Docker Compose
    + the results are saved in a folder on the host machine
    + the parameters of the experiments can be parametrized via environment variables
    + if the experiments for a given assignment of paramenters are already executed, 
    the script should recognize it and skip the execution

3. Put your solution in a new repository and share its link with me [via email](mailto:giovanni.ciatto@unibo.it)

