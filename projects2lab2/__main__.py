"""An AWS Python Pulumi program"""
import pulumi , pulumi_aws as aws , json 

mycfg=pulumi.Config()

vpc2=aws.ec2.Vpc(
    "vpc2",
 aws.ec2.VpcArgs(
        cidr_block=mycfg.get_secret(key="vpc2block"),
        tags={
            "Name": "vpc2",
        },
    )
)

intgw1=aws.ec2.InternetGateway(
    "intgw1",
 aws.ec2.InternetGatewayArgs(
        vpc_id=vpc2.id,
        tags={
            "Name": "intgw1",
        },
    )
)

public_subnet_names=[ "pub1sub1" ,  "pub2ub2"]
zones=["us-east-1a" , "us-east-1b" ]
pb1_cidr1=mycfg.get_secret(key="pub1")
pb2_cidr2=mycfg.get_secret(key="pub2")
pbcidrs=[ pb1_cidr1 ,  pb2_cidr2]
for allpub in range(len(public_subnet_names)): 
    public_subnet_names[allpub]=aws.ec2.Subnet(
        public_subnet_names[allpub],
        aws.ec2.SubnetArgs(
            vpc_id=vpc2.id,
            cidr_block=pbcidrs[allpub],
            availability_zone=zones[allpub],
            map_public_ip_on_launch=True,
            tags={
                "Name": public_subnet_names[allpub],
            },
        )
    )
    
    
web_subnet_names=[ "web1sub1" ,  "web2ub2"]
web_cidr1=mycfg.get_secret(key="web1")
web_cidr2=mycfg.get_secret(key="web2")
wbcidrs=[ web_cidr1 , web_cidr2]
for allweb in range(len(web_subnet_names)): 
    web_subnet_names[allweb]=aws.ec2.Subnet(
        web_subnet_names[allweb],
        aws.ec2.SubnetArgs(
            vpc_id=vpc2.id,
            cidr_block=wbcidrs[allweb],
            availability_zone=zones[allweb],
            tags={
                "Name": web_subnet_names[allweb],
            },
        )
    )
    
db_subnet_names=[ "db1sub1" ,  "db2ub2"]
db1_cidr1=mycfg.get_secret(key="dbase1")
db2_cidr2=mycfg.get_secret(key="dbase2")
dbcidrs=[ db1_cidr1, db2_cidr2]
for alldb in range(len(db_subnet_names)): 
    db_subnet_names[alldb]=aws.ec2.Subnet(
        db_subnet_names[alldb],
        aws.ec2.SubnetArgs(
            vpc_id=vpc2.id,
            cidr_block=wbcidrs[alldb],
            availability_zone=zones[alldb],
            tags={
                "Name": web_subnet_names[alldb],
            },
        )
    )
    
table1=aws.ec2.RouteTable(
    "table1",
    aws.ec2.RouteTableArgs(
        vpc_id=vpc2.id ,
        routes=[
            aws.ec2.RouteTableRouteArgs(
                cidr_block=mycfg.get_secret(key="traffic_any"),
                gateway_id=intgw1.id
            )
        ],
        tags={
            "Name": "table1",
        }
    ) 
 ) 

allink1=["pblink1a" ,  "pblink1b"]
for allpbattach1 in  range(len(allink1)):
    allink1[allpbattach1]=aws.ec2.RouteTableAssociation(
        allink1[allpbattach1],
        aws.ec2.RouteTableAssociationArgs(
            subnet_id=public_subnet_names[allpbattach1].id,
            route_table_id=table1.id
        )
    )
    
eips=["eip1a" ,  "eip1b"]
for alleip in range(len(eips)):
    eips[alleip]=aws.ec2.Eip(
        eips[alleip],
        aws.ec2.EipArgs(
        domain="vpc",
        tags={
            "Name": eips[alleip],
        }
        )
    )

natgwlists=["natgw1a" ,  "natgw1b"]
for allnat in range(len(natgwlists)):
    natgwlists[allnat]=aws.ec2.NatGateway(
        natgwlists[allnat],
        aws.ec2.NatGatewayArgs(
            allocation_id=eips[allnat].id,
            subnet_id=public_subnet_names[allnat].id,
            tags={
                "Name": natgwlists[allnat],
            },
            connectivity_type="public"
        )
    )
    
table2=aws.ec2.RouteTable(
    "table2",
    aws.ec2.RouteTableArgs(
        vpc_id=vpc2.id ,
        routes=[
            aws.ec2.RouteTableRouteArgs(
                cidr_block=mycfg.get_secret(key="traffic_any"),
                nat_gateway_id=natgwlists[0].id
            )
        ],
        tags={
            "Name": "table2",
        }
    )
)

allink2=["wblink1a" ,  "dblink1a"]
subnetlink2=[ web_subnet_names[0].id , db_subnet_names[0].id]
for allattach2 in  range(len(allink2)):
    allink1[allattach2]=aws.ec2.RouteTableAssociation(
        allink1[allattach2],
        aws.ec2.RouteTableAssociationArgs(
            subnet_id=subnetlink2[allattach2],
            route_table_id=table2.id
        )
    )

table3=aws.ec2.RouteTable(
    "table3",
    aws.ec2.RouteTableArgs(
        vpc_id=vpc2.id ,
        routes=[
            aws.ec2.RouteTableRouteArgs(
                cidr_block=mycfg.get_secret(key="traffic_any"),
                nat_gateway_id=natgwlists[1].id
            )
        ],
        tags={
            "Name": "table3",
        }
    )
)

allink3=["wblink1b" ,  "dblink1b"]
subnetlink3=[ web_subnet_names[1].id , db_subnet_names[1].id]
for allattach3 in  range(len(allink3)):
    allink3[allattach3]=aws.ec2.RouteTableAssociation(
        allink3[allattach3],
        aws.ec2.RouteTableAssociationArgs(
            subnet_id=subnetlink3[allattach3],
            route_table_id=table3.id
        )
    )
    
    
nacls1=aws.ec2.NetworkAcl(
    "nacls1",
    aws.ec2.NetworkAclArgs(
         vpc_id=vpc2.id, 
          ingress=[
              aws.ec2.NetworkAclIngressArgs(
                  from_port=22,
                  to_port=22,
                  protocol="tcp",
                  cidr_block=mycfg.get_secret(key="myips"),
                  action="allow",
                  icmp_code=0,
                  icmp_type=0,
                  rule_no=100
              ),
              aws.ec2.NetworkAclIngressArgs(
                  from_port=22,
                  to_port=22,
                  protocol="tcp",
                  cidr_block=mycfg.get_secret(key="traffic_any"),
                  action="deny",
                  icmp_code=0,
                  icmp_type=0,
                  rule_no=101
              ),
              aws.ec2.NetworkAclIngressArgs(
                  from_port=80,
                  to_port=80,
                  protocol="tcp",
                  cidr_block=mycfg.get_secret(key="traffic_any"),
                  action="allow",
                  icmp_code=0,
                  icmp_type=0,
                  rule_no=200
              ),
              aws.ec2.NetworkAclIngressArgs(
                  from_port=443,
                  to_port=443,
                  protocol="tcp",
                  cidr_block=mycfg.get_secret(key="traffic_any"),
                  action="allow",
                  icmp_code=0,
                  icmp_type=0,
                  rule_no=300
              ),
              aws.ec2.NetworkAclIngressArgs(
                  from_port=3306,
                  to_port=3306,
                  protocol="tcp",
                  cidr_block=db_subnet_names[0].id,
                  action="allow",
                  icmp_code=0,
                  icmp_type=0,
                  rule_no=400
              ),
               aws.ec2.NetworkAclIngressArgs(
                  from_port=3306,
                  to_port=3306,
                  protocol="tcp",
                  cidr_block=db_subnet_names[1].id,
                  action="allow",
                  icmp_code=0,
                  icmp_type=0,
                  rule_no=401
              ),
              aws.ec2.NetworkAclIngressArgs(
                  from_port=32768,
                  to_port=65535,
                  protocol="tcp",
                  cidr_block=mycfg.get_secret(key="traffic_any"),
                  action="allow",
                  icmp_code=0,
                  icmp_type=0,
                  rule_no=500
              ),
             aws.ec2.NetworkAclIngressArgs(
                  from_port=0,
                  to_port=0,
                  protocol="-1",
                  cidr_block=mycfg.get_secret(key="traffic_any"),
                  action="allow",
                  icmp_code=0,
                  icmp_type=0,
                  rule_no=600
              ),  
          ],
          egress=[
              aws.ec2.NetworkAclEgressArgs(
                  from_port=22,
                  to_port=22,
                  protocol="tcp",
                  cidr_block=mycfg.get_secret(key="myips"),
                  action="allow",
                  icmp_code=0,
                  icmp_type=0,
                  rule_no=100
              ),
              aws.ec2.NetworkAclEgressArgs(
                  from_port=22,
                  to_port=22,
                  protocol="tcp",
                  cidr_block=mycfg.get_secret(key="traffic_any"),
                  action="deny",
                  icmp_code=0,
                  icmp_type=0,
                  rule_no=101
              ),
              aws.ec2.NetworkAclEgressArgs(
                  from_port=80,
                  to_port=80,
                  protocol="tcp",
                  cidr_block=mycfg.get_secret(key="traffic_any"),
                  action="allow",
                  icmp_code=0,
                  icmp_type=0,
                  rule_no=200
              ),
              aws.ec2.NetworkAclEgressArgs(
                  from_port=443,
                  to_port=443,
                  protocol="tcp",
                  cidr_block=mycfg.get_secret(key="traffic_any"),
                  action="allow",
                  icmp_code=0,
                  icmp_type=0,
                  rule_no=300
              ),
              aws.ec2.NetworkAclEgressArgs(
                  from_port=3306,
                  to_port=3306,
                  protocol="tcp",
                  cidr_block=db_subnet_names[0].id,
                  action="allow",
                  icmp_code=0,
                  icmp_type=0,
                  rule_no=400
              ),
               aws.ec2.NetworkAclEgressArgs(
                  from_port=3306,
                  to_port=3306,
                  protocol="tcp",
                  cidr_block=db_subnet_names[1].id,
                  action="allow",
                  icmp_code=0,
                  icmp_type=0,
                  rule_no=401
              ),
              aws.ec2.NetworkAclEgressArgs(
                  from_port=32768,
                  to_port=65535,
                  protocol="tcp",
                  cidr_block=mycfg.get_secret(key="traffic_any"),
                  action="allow",
                  icmp_code=0,
                  icmp_type=0,
                  rule_no=500
              ),
             aws.ec2.NetworkAclEgressArgs(
                  from_port=0,
                  to_port=0,
                  protocol="-1",
                  cidr_block=mycfg.get_secret(key="traffic_any"),
                  action="allow",
                  icmp_code=0,
                  icmp_type=0,
                  rule_no=600
              ),   
          ],
          tags={
              "Name" :  "Nacls1"
          } 
    )
)

allsubnets=[ public_subnet_names[allpub].id , web_subnet_names[allweb].id , db_subnet_names[alldb].id ]
for allacl in range(len(allsubnets)):
    allsubnets[allacl]=aws.ec2.NetworkAclAssociation(
            allsubnets[allacl],
            aws.ec2.NetworkAclAssociationArgs(
            network_acl_id=nacls1.id,
            subnet_id=allsubnets[allacl]
        )
    )
    
lbsecurity=aws.ec2.SecurityGroup(
     "lbsecurity",
     aws.ec2.SecurityGroupArgs(
         vpc_id=vpc2.id ,
         name="lbsecure",
         ingress=[
             aws.ec2.SecurityGroupIngressArgs(
                 from_port=80,
                 to_port=80,
                 protocol="tcp",
                 cidr_blocks=mycfg.get_secret(key="traffic_any"),
                 description="http",
                ),
             aws.ec2.SecurityGroupIngressArgs(
                 from_port=443,
                 to_port=443,
                 protocol="tcp",
                 cidr_blocks=mycfg.get_secret(key="traffic_any"),
                 description="https",
                ),
         ],
         egress=[
            aws.ec2.SecurityGroupEgressArgs(
                 from_port=0,
                 to_port=0,
                 protocol="-1",
                 cidr_blocks=mycfg.get_secret(key="traffic_any")
             )
         ],
         tags={
             "Name": "lbsecurity"
         }
     ))
    


   
websecurity=aws.ec2.SecurityGroup(
     "websecurity",
     aws.ec2.SecurityGroupArgs(
         vpc_id=vpc2.id ,
         name="websecure",
         ingress=[
             aws.ec2.SecurityGroupIngressArgs(
                 from_port=32768,
                 to_port=65535,
                 protocol="tcp",
                 security_groups=[lbsecurity.id]
                ),
         ],
         egress=[
            aws.ec2.SecurityGroupEgressArgs(
                 from_port=0,
                 to_port=0,
                 protocol="-1",
                 cidr_blocks=mycfg.get_secret(key="traffic_any")
             )
         ],
         tags={
             "Name": "websecurity"
         }
     ))


dbsecurity=aws.ec2.SecurityGroup(
     "dbsecurity",
     aws.ec2.SecurityGroupArgs(
         vpc_id=vpc2.id ,
         name="dbsecure",
         ingress=[
             aws.ec2.SecurityGroupIngressArgs(
                 from_port=3306,
                 to_port=3306,
                 protocol="tcp",
                 security_groups=[websecurity.id]
                ),
         ],
         egress=[
            aws.ec2.SecurityGroupEgressArgs(
                 from_port=0,
                 to_port=0,
                 protocol="-1",
                 cidr_blocks=mycfg.get_secret(key="traffic_any")
             )
         ],
         tags={
             "Name": "dbsecurity"
         }
     ))

targetgrp1=aws.lb.TargetGroup(
  "targetgrp1",
  aws.lb.TargetGroupArgs(
    port=80,
    protocol="HTTP",
    load_balancing_algorithm_type="round_robin",
    vpc_id=vpc2.id,
    target_type="instance",
    health_check=aws.lb.TargetGroupHealthCheckArgs(
         enabled=True,
         interval=30,
         path="/",
         port="traffic-port",
         protocol="HTTP",
         timeout=15,
         unhealthy_threshold=6,
         healthy_threshold=3,
         matcher="200-599"
       ),
    tags={
      "Name" : "targetgrp1"
    }
  )
)
alb1=aws.lb.LoadBalancer(
  "alb1",
  aws.lb.LoadBalancerArgs(
     idle_timeout=180,
     ip_address_type="ipv4",
     load_balancer_type="application",
     name="alb1",
     security_groups=[lbsecurity.id],
     subnets=[public_subnet_names[allpub].id],
     tags={
       "Name" : "alb1"
     },
  )
)

listener1=aws.lb.Listener(
  "listener1",
  aws.lb.ListenerArgs(
    load_balancer_arn=alb1.arn,
    port=80,
    protocol="HTTP",
    default_actions=[
      aws.lb.ListenerDefaultActionArgs(
        type="forward",
        target_group_arn=targetgrp1.arn
      )
    ]
  )
)
  
rule1=aws.lb.ListenerRule(
  "rule1",
  aws.lb.ListenerRuleArgs(
    listener_arn=listener1.arn,
    priority=10,
    actions=[
      aws.lb.ListenerRuleActionArgs(
        type="forward",
        target_group_arn=targetgrp1.arn
      )
    ],
    conditions=[
       aws.lb.ListenerRuleConditionArgs(
         http_request_method= aws.lb.ListenerRuleConditionHttpRequestMethodArgs(
              values=["GET","POST"]
           )
           )],
    tags={
      "Name" : "rule1"
    }
       )
  )

instrole=aws.iam.Role(
    "instrole",
    aws.iam.RoleArgs(
        name="instrole",
        assume_role_policy=json.dumps({
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": mycfg.get_secret(key="assumepolicy"),
                    "Principal": {
                        "Service": "ec2.amazonaws.com"
                    },
                    "Effect": "Allow",
                }
            ]
        })
    )

)

instpolicy=aws.iam.Policy(
    "instpolicy",
    aws.iam.PolicyArgs(
        name="instpolicy",
        policy=json.dumps({
        "Version": "2012-10-17",
        "Statement": [{
           "Action": [
        "ecs:DeregisterContainerInstance",
        "ecs:DeregisterTaskDefinition",
        "ecs:DescribeClusters",
        "ecs:DescribeContainerInstances",
        "ecs:DescribeServices",
        "ecs:DescribeTaskDefinition",
        "ecs:DiscoverPollEndpoint",
        "ecs:Poll",
        "ecs:RegisterContainerInstance",
        "ecs:RegisterTaskDefinition",
        "ecs:StartTelemetrySession",
        "ecs:Submit*",
        "ecs:DescribeTaskDefinition",
        "ec2:DescribeTags",
        "ecs:TagResource"   
                    ],
                    "Effect": "Allow",
                    "Resource": "*"
                }
            ]
        })
    )
)

instattach1=aws.iam.RolePolicyAttachment(
    "instattach1",
    aws.iam.RolePolicyAttachmentArgs(
        role=instrole.name,
        policy_arn=instpolicy.arn
    )
)
instattach2=aws.iam.RolePolicyAttachment(
    "instattach2",
    aws.iam.RolePolicyAttachmentArgs(
        role=instrole.name,
        policy_arn=aws.iam.ManagedPolicy.AMAZON_SSM_MANAGED_EC2_INSTANCE_DEFAULT_POLICY
    )
)


ecsrole=aws.iam.Role(
    "ecsrole",
    aws.iam.RoleArgs(
        name="ecsrole",
        assume_role_policy=json.dumps({
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": mycfg.get_secret(key="assumepolicy"),
                    "Principal": {
                        "Service": "ecs.amazonaws.com"
                    },
                    "Effect": "Allow",
                }
            ]
        })
    )
)



tasksrole=aws.iam.Role(
    "instrole",
    aws.iam.RoleArgs(
        name="instrole",
        assume_role_policy=json.dumps({
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": mycfg.get_secret(key="assumepolicy"),
                    "Principal": {
                        "Service": "esc-tasks.amazonaws.com"
                    },
                    "Effect": "Allow",
                }
            ]
        })
    )
)

ecspolicy=aws.iam.Policy(
    "ecspolicy",
    aws.iam.PolicyArgs(
        name="ecspolicy",
        policy=json.dumps({
        "Version": "2012-10-17",
        "Statement": [{
           "Effect": "Allow",
           "Action": [
        "elasticloadbalancing:DeregisterTargets",
        "elasticloadbalancing:DescribeListeners",
        "elasticloadbalancing:DescribeLoadBalancers",
        "elasticloadbalancing:DescribeRules",
        "elasticloadbalancing:DescribeTargetGroups",
        "elasticloadbalancing:RegisterTargets",
        "elasticloadbalancing:DescribeTargetHealth",
        "ec2:DescribeInstanceStatus",
        "ec2:DescribeInstances",
        "ec2:DescribeTags"
               ],
        "Resource" : "*"

           }]
        })
    )
)


ecsattqch1=aws.iam.RolePolicyAttachment(
    "ecsattqch1",
    aws.iam.RolePolicyAttachmentArgs(
        role=ecsrole.name,
        policy_arn=ecspolicy.arn
    )
)

tasks_attqch2=aws.iam.RolePolicyAttachment(
    "tasks_attqch2",
    aws.iam.RolePolicyAttachmentArgs(
        role=tasksrole.name,
        policy_arn=aws.iam.ManagedPolicy.AMAZON_EC2_CONTAINER_REGISTRY_FULL_ACCESS
    )
)

tasks_attqch3=aws.iam.RolePolicyAttachment(
    "tasks_attqch3",
    aws.iam.RolePolicyAttachmentArgs(
        role=tasksrole.name,
        policy_arn=aws.iam.ManagedPolicy.CLOUD_WATCH_LOGS_FULL_ACCESS
    )
)


cluster1=aws.ecs.Cluster(
    "cluster1",
    aws.ecs.ClusterArgs(
         name="cluster1",
         settings=[
             aws.ecs.ClusterSettingArgs(
                 name="containerInsights",
                 value="enabled"
             )
         ],
        tags={
            "Name" : "cluster1"
        }
    )
)

tasfdef1=aws.ecs.TaskDefinition(
    "tasfdef1",
    aws.ecs.TaskDefinitionArgs(
        family="tasfdef1",
        cpu="256",
        memory="512",
        requires_compatibilities=["EC2"],
        task_role_arn=tasksrole.arn,
        container_definitions=json.dumps([
            {
                "name": "site1",
                "image": "wordpress:latest",
                "essential": True,
                "portMappings": [
                    {
                    "containerPort": 8000,
                    }
                ],
                "memory": 512,
                "cpu": 256
            }
        ]),
        volumes=aws.ecs.TaskDefinitionVolumeArgs(
                name="service-storage",
                host_path="/ecs/service-storage"
                )
            )
        )
        
services1=aws.ecs.Service(
    "services1",
    aws.ecs.ServiceArgs(
        cluster=cluster1.id,
        task_definition=tasfdef1.arn,
        iam_role=ecsrole.arn,
        desired_count=2,
        launch_type="EC2",
        load_balancers=[aws.ecs.ServiceLoadBalancerArgs(
            target_group_arn=targetgrp1.arn,
            container_name="site1",
            container_port=8000
        )],
        tags={
            "Name" : "services1"
        },
        health_check_grace_period_seconds=300
    ),
    opts=pulumi.ResourceOptions(depends_on=[ecsattqch1])

)

profile2=aws.iam.InstanceProfile(
    "profile2",
    aws.iam.InstanceProfileArgs(
    name="profile2",
    role=instrole.name
    )
)

temp3=aws.ec2.LaunchTemplate(
    "temp3",
    aws.ec2.LaunchTemplateArgs(
    image_id="",
    instance_type="",
    vpc_security_group_ids=[websecurity.id],
    block_device_mappings=[
        aws.ec2.LaunchTemplateBlockDeviceMappingArgs(
            device_name="/dev/sdq1",
            ebs=aws.ec2.LaunchTemplateBlockDeviceMappingEbsArgs(
                    volume_size=8,
                    volume_type="gp2",
                    encrypted="false",
                    delete_on_termination=True
                )
        )
    ],
    iam_instance_profile=aws.ec2.LaunchTemplateIamInstanceProfileArgs(name=profile2.name)
    )
)

scalegrp=aws.autoscaling.Group(
 "scalegrp",
  aws.autoscaling.GroupArgs(
  name="scale3",
  min_size=1,
  desired_capacity=2,
  max_size=4,
  vpc_zone_identifiers=[web_subnet_names[allweb].id],
  health_check_grace_period=600,
  health_check_type="ELB",
  launch_template=aws.autoscaling.GroupLaunchTemplateArgs(
    id=temp3.id , 
    version="$Latest"
  ),
  )
)

# ssm session manager

ssm1list=aws.ssm.Document(
  "ssm1list",
  aws.ssm.DocumentArgs(
  name="doctarget",
  document_format="YAML",
  document_type="Command",
  content="""schemaVersion: '1.2'
description: Check ip configuration of a Linux instance.
parameters: {}
runtimeConfig:
  'aws:runShellScript':
    properties:
      - id: '0.aws:runShellScript'
        runCommand:
          - sudo su 
          - sudo apt update -y && sudo apt upgrade -y 
          - sudo apt install -y docker.io awscli mysql-server
          - sudo curl -O https://s3.us-east-1.amazonaws.com/amazon-ecs-agent-us-east-1/amazon-ecs-init-latest.amd64.deb 
          - sudo dpkg -i amazon-ecs-init-latest.amd64.deb
          - sudo systemctl enable amazon-ssm-agent --now
          - sudo systemctl enable docker --now 
          - sudo systemctl enable ecs --now
          - sudo systemctl enable mysql --now
          - sudo usermod -aG docker ubuntu 
          - sudo echo ECS_CLUSTER="cluster1" >> /etc/ecs/ecs.config 
        
"""
  )
)

insttargets=aws.ssm.Association(
   "insttargets",
   aws.ssm.AssociationArgs(
       name=ssm1list.name,
       association_name="instssmtargets",
       document_version=ssm1list.document_version,
       targets=[aws.ssm.AssociationTargetArgs(
           key="InstanceIds",
           values=["*"]
       )],
   )
)


dbsubnetgrp1=aws.rds.SubnetGroup(
  "dbsubnetgrp1",
  aws.rds.SubnetGroupArgs(
    name="dbsubnetgrp1",
    subnet_ids=[db_subnet_names[alldb].id],
    tags={
      "Name" : "dbsubnetgrp1"
    }
  )
)
  
dbase=aws.rds.Instance(
  "dbase",
  aws.rds.InstanceArgs(
    db_name="sitedb",
    allocated_storage=20,
    max_allocated_storage=40,
    engine="mysql",
    engine_version="8.0",
    instance_class="db.t3.micro",
    username=mycfg.get_secret(key="dbuser"),
    password=mycfg.get_secret(key="dbpasswords"),
    skip_final_snapshot=True,
    db_subnet_group_name=dbsubnetgrp1.name,
    vpc_security_group_ids=[dbsecurity.id],
    tags={
      "Name" : "dbase"
    },
    allow_major_version_upgrade=True,
    multi_az=True,
    auto_minor_version_upgrade=True,
    apply_immediately=True,
    backup_retention_period=0,
    delete_automated_backups=True,
    deletion_protection=False,
    storage_type="gp2",
    storage_encrypted=False,
    backup_window="09:00-11:00",
    maintenance_window="Fri:00:00-Fri:05:00",
  )
)