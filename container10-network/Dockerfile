# Use Amazon Linux base image
FROM amazonlinux:2023

# Set working directory
WORKDIR /root

# Update packages and install essential tools
RUN yum -y update && \
    yum install -y aws-cli python3-pip python3-wheel && \
    pip install networkx pandas igraph leidenalg
	
# Copy your bash script into the container
COPY network.bash /root/

# Make the script executable
RUN chmod +x /root/network.bash
