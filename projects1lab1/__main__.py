"""An AWS Python Pulumi program"""
import pulumi,json , pulumi_aws as aws 

cfg1=pulumi.Config()
vpc1=aws.ec2.Vpc(
  "vpc1" ,
  aws.ec2.VpcArgs(
      cidr_block=cfg1.get_secret(key="vpcblock1"),
      tags={
          "Name" : "vpc1"
      }
  )
)

intgw1=aws.ec2.InternetGateway(
  "intgw1",
   aws.ec2.InternetGatewayArgs(
      vpc_id=vpc1.id,
      tags={
        "Name" :  "intgw1"
      }
   ))

pbsubnetsnames=["pub1sub1" ,  "pub2sub2" ]
zones=["us-east-1a" , "us-east-1b" ]
pbcidr1=cfg1.get_secret(key="public1cidr")
pbcidr2=cfg1.get_secret(key="public2cidr")
pbcidr3=cfg1.get_secret(key="public3cidr")
allpbcidrs=[pbcidr1 , pbcidr2 , pbcidr3]
for allpub in range(len(pbsubnetsnames)):
    pbsubnetsnames[allpub]=aws.ec2.Subnet(
        pbsubnetsnames[allpub] ,
        aws.ec2.SubnetArgs(
            vpc_id=vpc1.id,
            cidr_block=allpbcidrs[allpub],
            availability_zone=zones[allpub],
            tags={
                "Name" : pbsubnetsnames[allpub]
            }
        )
    )

websubnetsnames=["web1sub1" , "web2sub2" ]
webcidr1=cfg1.get_secret(key="wb1cidr1")
webcidr2=cfg1.get_secret(key="wb2cidr2")
webcidr3=cfg1.get_secret(key="wb3cidr3")
webcidrs=[webcidr1 , webcidr2 , webcidr3]
for allweb in range(len(websubnetsnames)):
    websubnetsnames[allweb]=aws.ec2.Subnet(
        websubnetsnames[allweb] ,
        aws.ec2.SubnetArgs(
            vpc_id=vpc1.id,
            cidr_block=webcidrs[allweb],
            availability_zone=zones[allweb],
            tags={
                "Name" : pbsubnetsnames[allweb]
            }
        )
    )

dbsubnetsnames=["db1sub1" , "db2sub2" ]
dbase1cidr1=cfg1.get_secret(key="db1cidr1")
dbase2cidr2=cfg1.get_secret(key="db2cidr2")
dbase3cidr3=cfg1.get_secret(key="db3cidr3")
dbcidrs=[dbase1cidr1 , dbase2cidr2 , dbase3cidr3]

for alldb in range(len(dbsubnetsnames)):
    dbsubnetsnames[alldb]=aws.ec2.Subnet(
        dbsubnetsnames[alldb] ,
        aws.ec2.SubnetArgs(
            vpc_id=vpc1.id,
            cidr_block=webcidrs[alldb],
            availability_zone=zones[alldb],
            tags={
                "Name" : pbsubnetsnames[alldb]
            }
        )
    )

table1=aws.ec2.RouteTable(
  "table1",
  aws.ec2.RouteTableArgs(
    vpc_id=vpc1.id , 
    routes=[
       aws.ec2.RouteTableRouteArgs(
         cidr_block=cfg1.get_secret(key="allow_any_traffic"),
         gateway_id=intgw1.id
       )
    ],
    tags={
      "Name" :  "table1"
    }
  )
)

pblink_lists1=["table1link1" , "table1link2"]
for allink1 in range(len(pblink_lists1)):
    pblink_lists1[allink1]=aws.ec2.RouteTableAssociation(
         pblink_lists1[allink1],
        aws.ec2.RouteTableAssociationArgs(
          route_table_id=table1.id,
          subnet_id=pbsubnetsnames[allpub].id
        )
)

myeips=["eip1" , "eip2"]
for alleips in range(len(myeips)):
    myeips[alleips]=aws.ec2.Eip(
       myeips[alleips],
       aws.ec2.EipArgs(
       domain="vpc",
       tags={
         "Name" : myeips[alleips]
        }
    )
)

eips=[myeips[0].id , myeips[1].id]
mypbs=[ pbsubnetsnames[0].id , pbsubnetsnames[1].id]
natlists=["natgw1" , "natgw2"]
for allnat in range(len(natlists)):
    natlists[allnat]=aws.ec2.NatGateway(
       natlists[allnat],
       aws.ec2.NatGatewayArgs(
         allocation_id=eips[allnat],
         subnet_id=mypbs[allnat],
         tags={
           "Name" : natlists[allnat]
         },
         connectivity_type="public"
    )
  )

natgws=[natlists[0].id , natlists[1].id ]
mytables=["table2" , "table3"]
for alltables in range(len(mytables)):
    mytables[alltables]=aws.ec2.RouteTable(
        mytables[alltables],
        aws.ec2.RouteTableArgs(
          vpc_id=vpc1.id,
          routes=[
            aws.ec2.RouteTableRouteArgs(
              cidr_block=cfg1.get_secret(key="allow_any_traffic"),
              nat_gateway_id=natgws[alltables]
            )
          ],
          tags={
            "Name" : mytables[alltables]
          }
        )
    )

wblists=[websubnetsnames[0].id , websubnetsnames[1].id]
dblists=[dbsubnetsnames[0].id , dbsubnetsnames[1].id]
tableslnk=[mytables[0].id , mytables[1].id]
tables_attach1=[ "tbattach4" , "tbattach5"]
tables_attach2=[ "tbattach6" , "tbattach7"]
for allattaches1 in range(len(tables_attach1)):
    tables_attach1[allattaches1]=aws.ec2.RouteTableAssociation(
        tables_attach1[allattaches1],
        aws.ec2.RouteTableAssociationArgs(
          route_table_id=tableslnk[allattaches1],
          subnet_id=wblists[allattaches1]
        )
    )
for allattaches2 in range(len(tables_attach2)):
        tables_attach2[allattaches2]=aws.ec2.RouteTableAssociation(
            tables_attach2[allattaches2],
            aws.ec2.RouteTableAssociationArgs(
              route_table_id=tableslnk[allattaches2],
              subnet_id=dblists[allattaches2]
            )
        )


lbsecurity=aws.ec2.SecurityGroup(
  "lbsecurity",
  aws.ec2.SecurityGroupArgs(
    name="lbsecure",
    vpc_id=vpc1.id,
    ingress=[
      aws.ec2.SecurityGroupIngressArgs(
        from_port=80,
        to_port=80,
        protocol="tcp",
        cidr_blocks=cfg1.get_secret(key="allow_any_traffic"),
      ),
      aws.ec2.SecurityGroupIngressArgs(
        from_port=443,
        to_port=443,
        protocol="tcp",
        cidr_blocks=cfg1.get_secret(key="allow_any_traffic"),
      )
    ],
    egress=[
      aws.ec2.SecurityGroupEgressArgs(
        from_port=0,
        to_port=0,
        protocol="-1",
        cidr_blocks=cfg1.get_secret(key="allow_any_traffic"),
      )
    ],
    tags={
      "Name" : "lbsecurity"
    }
  )
)
websecurity=aws.ec2.SecurityGroup(
  "websecurity",
  aws.ec2.SecurityGroupArgs(
    name="websecure",
    vpc_id=vpc1.id,
    ingress=[
      aws.ec2.SecurityGroupIngressArgs(
        from_port=1024,
        to_port=65535,
        protocol="tcp",
        security_groups=[lbsecurity.id],
      ),
    ],
    egress=[
      aws.ec2.SecurityGroupEgressArgs(
        from_port=0,
        to_port=0,
        protocol="-1",
        cidr_blocks=cfg1.get_secret(key="allow_any_traffic"),
      )
    ],
    tags={
      "Name" : "websecurity"
    }
  )
)
  
dbsecurity=aws.ec2.SecurityGroup(
  "dbsecurity",
  aws.ec2.SecurityGroupArgs(
    name="dbsecure",
    vpc_id=vpc1.id,
    ingress=[
      aws.ec2.SecurityGroupIngressArgs(
        from_port=3306,
        to_port=3306,
        protocol="tcp",
        security_groups=[websecurity.id],
      )
    ],
    egress=[
      aws.ec2.SecurityGroupEgressArgs(
        from_port=0,
        to_port=0,
        protocol="-1",
        cidr_blocks=cfg1.get_secret(key="allow_any_traffic"),
      )
    ],
    tags={
      "Name" : "dbsecurity"
    }
  )
)
targetgrp=aws.lb.TargetGroup(
  "targetgrp",
  aws.lb.TargetGroupArgs(
    port=80,
    protocol="HTTP",
    load_balancing_algorithm_type="round_robin",
    vpc_id=vpc1.id,
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
      "Name" : "targetgrp"
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
     subnets=[pbsubnetsnames[allpub].id],
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
        target_group_arn=targetgrp.arn
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
        target_group_arn=targetgrp.arn
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
nacl1=aws.ec2.NetworkAcl(
   "nacl1",
   aws.ec2.NetworkAclArgs(
     vpc_id=vpc1.id,
     tags={
       "Name" : "nacl1"
     },
     ingress=[
       aws.ec2.NetworkAclIngressArgs(
         from_port=22,
         to_port=22,
         rule_no=100,
         action="allow",
         protocol="tcp",
         cidr_block=cfg1.get_secret(key="myips")
       ),
       aws.ec2.NetworkAclIngressArgs(
         from_port=22,
         to_port=22,
         rule_no=101,
         action="deny",
         protocol="tcp",
         cidr_block=cfg1.get_secret(key="allow_any_traffic"),
       ),
        aws.ec2.NetworkAclIngressArgs(
         from_port=80,
         to_port=80,
         rule_no=200,
         action="allow",
         protocol="tcp",
         cidr_block=cfg1.get_secret(key="allow_any_traffic"),
       ),
        aws.ec2.NetworkAclIngressArgs(
         from_port=443,
         to_port=443,
         rule_no=300,
         action="allow",
         protocol="tcp",
         cidr_block=cfg1.get_secret(key="allow_any_traffic"),
       ),
        aws.ec2.NetworkAclIngressArgs(
         from_port=3306,
         to_port=3306,
         rule_no=400,
         action="allow",
         protocol="tcp",
         cidr_block=dbsubnetsnames[0].cidr_block,
       ),
         aws.ec2.NetworkAclIngressArgs(
         from_port=3306,
         to_port=3306,
         rule_no=401,
         action="allow",
         protocol="tcp",
         cidr_block=dbsubnetsnames[1].cidr_block,
       ),
        aws.ec2.NetworkAclIngressArgs(
         from_port=0,
         to_port=0,
         rule_no=500,
         action="allow",
         protocol="-1",
         cidr_block=cfg1.get_secret(key="allow_any_traffic"),
       ),
     ],
     egress=[
       aws.ec2.NetworkAclEgressArgs(
         from_port=22,
         to_port=22,
         rule_no=100,
         action="allow",
         protocol="tcp",
         cidr_block=cfg1.get_secret(key="myips")
       ),
       aws.ec2.NetworkAclEgressArgs(
         from_port=22,
         to_port=22,
         rule_no=101,
         action="deny",
         protocol="tcp",
         cidr_block=cfg1.get_secret(key="allow_any_traffic"),

       ),
       aws.ec2.NetworkAclEgressArgs(
         from_port=80,
         to_port=80,
         rule_no=200,
         action="allow",
         protocol="tcp",
         cidr_block=cfg1.get_secret(key="allow_any_traffic"),
       ),
       aws.ec2.NetworkAclEgressArgs(
         from_port=443,
         to_port=443,
         rule_no=300,
         action="allow",
         protocol="tcp",
         cidr_block=cfg1.get_secret(key="allow_any_traffic"),
       ),
        aws.ec2.NetworkAclEgressArgs(
         from_port=3306,
         to_port=3306,
         rule_no=400,
         action="allow",
         protocol="tcp",
         cidr_block=dbsubnetsnames[0].cidr_block,
       ),
       aws.ec2.NetworkAclEgressArgs(
         from_port=3306,
         to_port=3306,
         rule_no=401,
         action="allow",
         protocol="tcp",
         cidr_block=dbsubnetsnames[1].cidr_block,
       ),
       aws.ec2.NetworkAclEgressArgs(
         from_port=0,
         to_port=0,
         rule_no=500,
         action="allow",
         protocol="-1",
         cidr_block=cfg1.get_secret(key="allow_any_traffic"),

       ),
     ]
   )
)

nacls_collect=["pbnacl1_link1","pbnacl1_link2" , "wbnacl1_link1","wbnacl1_link2"  , "dbnacl1_link1","dbnacl1_link2" ]
nacl_subnets=[pbsubnetsnames[0].id , pbsubnetsnames[1].id , websubnetsnames[0].id , websubnetsnames[1].id , dbsubnetsnames[0].id , dbsubnetsnames[1].id]

for allnacls in range(len(nacls_collect)):
    nacls_collect[allnacls]=aws.ec2.NetworkAclAssociation(
        nacls_collect[allnacls],
        aws.ec2.NetworkAclAssociationArgs(
          network_acl_id=nacl1.id,
          subnet_id=nacl_subnets[allnacls]
        )
    )


ssmrole=aws.iam.Role(
  "ssmrole",
   aws.iam.RoleArgs(
     name="ssmrole",
     assume_role_policy=json.dumps({
       "Version" : "2012-10-17",
       "Statement": [{
          "Effect" : "Allow",
          "Action" : cfg1.get_secret(key="assumerole"),
          "Principal" : {
            "Service" : "ec2.amazonaws.com"
          }
       }] 
     })
  )
)

attach1ssm=aws.iam.RolePolicyAttachment(
  "attach1ssm",
  aws.iam.RolePolicyAttachmentArgs(
    role=ssmrole.name,
    policy_arn=aws.iam.ManagedPolicy.AMAZON_SSM_MANAGED_EC2_INSTANCE_DEFAULT_POLICY
  )
)

temp1=aws.ec2.LaunchTemplate(
  "temp1",
  aws.ec2.LaunchTemplateArgs(
    name="temp1",
    image_id="ami-0e86e20dae9224db8",
    instance_type="t2.micro",
    vpc_security_group_ids=[websecurity.id],
    key_name="",
    block_device_mappings=[
      aws.ec2.LaunchTemplateBlockDeviceMappingArgs(
        device_name="/dev/sdm1",
        ebs=aws.ec2.LaunchTemplateBlockDeviceMappingEbsArgs(
          volume_size=8,
          volume_type="gp2",
          encrypted=False,
          delete_on_termination=True
        )
      )],
    tags={
      "Name" : "temp1"
    }
  )
)
  
scalegrp1=aws.autoscaling.Group(
   "scalegrp1",
   aws.autoscaling.GroupArgs(
     name="scalegrp1",
     vpc_zone_identifiers=[websubnetsnames[allweb].id],
     launch_template=aws.autoscaling.GroupLaunchTemplateArgs(
       id=temp1.id,
       version="$Latest"
     ),
     min_size=1,
     max_size=9,
     desired_capacity=3,
     
   )
)

scaleattachment=aws.autoscaling.Attachment(
  "scaleattachment",
  aws.autoscaling.AttachmentArgs(
    autoscaling_group_name=scalegrp1.name,
    lb_target_group_arn=targetgrp.arn
  )
)

ssmdoc1=aws.ssm.Document(
  "ssmdoc1",
  aws.ssm.DocumentArgs(
    name="ssmdoc1",
    document_type="Command",
    version_name="doc1ssm",
    document_format="YAML",
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
          - oudo touch installpackages.sh
          - sudo chmod +x installpackages.sh
          - sudo echo "install=$(sudo apt install net-tools mysql-server python3 -y)" >> installpackages.sh
          - sudo echo "$install" >> installpackages.sh
          - sudo ./installpackages.sh
          - sudo systemctl enable mysql --now 
          - sudo systemctl enable amazon-ssm-agent --now
          
"""
  ))

ssmlink=aws.ssm.Association(
  "ssmlink",
  aws.ssm.AssociationArgs(
    name="ssmlink",
    document_version=ssmdoc1.schema_version,
    association_name="ssmlink",
    targets=[
      aws.ssm.AssociationTargetArgs(
        key="InstanceIds",
        values=["*"]
      )
    ]
  )
)
  
instance_attach1=aws.iam.RolePolicyAttachment(
  "instance_attach1",
  aws.iam.RolePolicyAttachmentArgs(
    role=ssmrole.name,
    policy_arn=aws.iam.ManagedPolicy.AMAZON_SSM_MANAGED_EC2_INSTANCE_DEFAULT_POLICY
  )
)  

cwlogs=aws.cloudwatch.LogGroup(
  "cwlogs",
   aws.cloudwatch.LogGroupArgs(
     name="cwlogs",
     skip_destroy=False,
     tags={
       "Name" : "cwlogs"
     },     
   )
)
flowrole=aws.iam.Role(
  "flowrole",
   aws.iam.RoleArgs(
     name="flowrole",
     assume_role_policy=json.dumps({
       "Version" : "2012-10-17",
       "Statement": [{
          "Effect" : "Allow",
          "Action" : cfg1.get_secret(key="assumerole"),
          "Principal" : {
            "Service" : "vpc-flow-logs.amazonaws.com"
          }
       }] 
     })
  )
)

flowpolicy=aws.iam.Policy(
  "flowpolicy",
   aws.iam.PolicyArgs(
     name="flowpolicy1",
     policy=json.dumps({
       "Version" :  "2012-10-17",
        "Statement" :[{
           "Effect" : "Allow",
           "Action" : [
              "logs:CreateLogStream",
              "logs:DescribeLogGroups",
              "logs:DescribeLogStreams",
              "logs:GetLogEvents",
              "logs:PutLogEvents" 
           ],
           "Resource" : cfg1.get_secret(key="flow_cwlogs")
        }]
     })
   )
)

attach1=aws.iam.RolePolicyAttachment(
  "attach1",
  aws.iam.RolePolicyAttachmentArgs(
    role=flowrole.name,
    policy_arn=flowpolicy.arn
  )
)
traffic_flows=aws.ec2.FlowLog(
  "traffic_flows",
  aws.ec2.FlowLogArgs(
    log_destination_type="cloud-watch-logs",
    log_destination=cwlogs.arn,
    tags={
      "Name" : "traffic_flows"
    },
    vpc_id=vpc1.id,
    traffic_type="ALL",
    iam_role_arn=flowrole.arn
  )
)

dbsubnetgrp1=aws.rds.SubnetGroup(
  "dbsubnetgrp1",
  aws.rds.SubnetGroupArgs(
    name="dbsubnetgrp1",
    subnet_ids=[dbsubnetsnames[alldb].id],
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
    username=cfg1.get_secret(key="dbuser"),
    password=cfg1.get_secret(key="dbpassword"),
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