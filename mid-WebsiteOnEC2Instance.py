#!/usr/bin/env python
from constructs import Construct
from cdktf import App, TerraformStack, TerraformOutput
from cdktf_cdktf_provider_aws.provider import AwsProvider
from cdktf_cdktf_provider_aws.instance import Instance
from cdktf_cdktf_provider_aws.data_aws_ami import DataAwsAmi
from cdktf_cdktf_provider_aws.security_group import SecurityGroup


 
class MyInfrastructure(TerraformStack):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, id)

        # define resources here
        AwsProvider(self, "AWS", region="us-east-1")

        ami = DataAwsAmi(self,"AmazonLinuxAmi", 
            most_recent = True, 
            owners = ["amazon"],

            filter=[
                    {
                        "name":"name", 
                        "values":["al2023-ami*"]
                    },
                    {
                        "name":"architecture", 
                        "values":["x86_64"]
                    },
                    {
                        "name":"virtualization-type", 
                        "values":["hvm"]
                    },
                    ])
        
        print("ami id:", ami.id)

        configure_file = "configure.sh"
        with open(configure_file) as file:
            install_script = file.read()

        allow_http = SecurityGroup(self, "Allow_HTTP",
                                   egress=[{
                                            "fromPort"       : 0,
                                            "toPort"         : 0,
                                            "protocol"       : "-1",
                                            "cidrBlocks"     : ["0.0.0.0/0"],
                                            "ipv6CidrBlocks" : ["::/0"],
                                   }],
                                   ingress=[{
                                       "description": "Allow HTTP traffic",
                                       "fromPort":80,
                                       "toPort":80,
                                       "cidrBlocks": ["0.0.0.0/0"],
                                       "protocol": "tcp"
                                   }, 
                                   {
                                       "description": "Allow SSH",
                                       "fromPort":22,
                                       "toPort":22,
                                       "cidrBlocks": ["50.235.238.194/32"],
                                       "protocol": "tcp"
                                   },
                                   ]                      
                                   )


        server = Instance(self, "WebServer", 
            ami=ami.id,
            instance_type="t3.large",
            user_data = install_script,
            vpc_security_group_ids=[allow_http.id],
            tags={"Name":"Webserver"} )

        TerraformOutput(self, "website_url",
                value="http://"+server.public_ip ,
                )

app = App()
MyInfrastructure(app, "cdktf_website")

app.synth()