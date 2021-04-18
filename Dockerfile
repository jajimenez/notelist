FROM python:3.9-slim

# Copy Notelist files
WORKDIR /usr/src/app
COPY . .

# Generate Notelist Wheel package and install it
RUN python setup.py bdist_wheel && \
    pip install ./dist/notelist-* && \
    rm -rf * && rm -f

# Create a Python script that sets the Notelist configuration
RUN echo 'from os import environ as env' >> config.py && \
    echo 'from notelist import config as conf\n' >> config.py && \
    echo 'if "DB_URI" in env:' >> config.py && \
    echo '    conf.set_config("0.0.0.0", 5000, env["DB_URI"])\n' >> config.py && \
    echo 'command = "notelist"\n' >> config.py && \
    echo 'if "ROOT_PASSWORD" in env:' >> config.py && \
    echo '    command += " --rp " + env["ROOT_PASSWORD"]\n' >> config.py && \
    echo 'with open("notelist.sh", "w") as f:'  >> config.py && \
    echo '    f.write(command + "\\n")' >> config.py

# Create a Bash script to run when the container starts
RUN echo 'python config.py' >> run.sh && \
    echo 'unset DB_URI' >> run.sh && \
    echo 'unset ROOT_PASSWORD' >> run.sh && \
    echo 'sh notelist.sh' >> run.sh

EXPOSE 5000
CMD ["sh", "run.sh"]
