"""An AWS Python Pulumi program"""
import pulumi , pulumi_aws as aws ,json 

cfg1=pulumi.Config()

vpc1=aws.ec2.Vpc(
    "vpc1",
    aws.ec2.VpcArgs(
        cidr_block=cfg1.require_secret(key="block1"),
        tags={
            "Name": "vpc1",
        },
    )
)

intgw1=aws.ec2.InternetGateway(
    "intgw1" , 
    aws.ec2.InternetGatewayArgs(
        vpc_id=vpc1.id,
        tags={
            "Name": "intgw1",
        },
    )
)

pbsubs=["public1","public2"]
zones=["us-east-1a","us-east-1b"]
pbcidr1=cfg1.require_secret("cidr1")
pbcidr2=cfg1.require_secret("cidr2")
pbcidrs=[pbcidr1,pbcidr2]
for allpbsub in range(len(pbsubs)):
    pbsubs[allpbsub]=aws.ec2.Subnet(
        pbsubs[allpbsub],
        aws.ec2.SubnetArgs(
            vpc_id=vpc1.id,
            cidr_block=pbcidrs[allpbsub],
            availability_zone=zones[allpbsub],
            map_public_ip_on_launch=True,
            tags={
                "kubernetes.io/role/elb": "1",
            }
        )
    )

ndsubs=["node1","node2"]
ndcidr1=cfg1.require_secret("cidr3")
ndcidr2=cfg1.require_secret("cidr4")
ndcidrs=[ndcidr1,ndcidr2]
for allndsub in range(len(ndsubs)):
    ndsubs[allndsub]=aws.ec2.Subnet(
        ndsubs[allndsub],
        aws.ec2.SubnetArgs(
            vpc_id=vpc1.id,
            cidr_block=ndcidrs[allndsub],
            availability_zone=zones[allndsub],
            tags={
                "kubernetes.io/role/internal-elb": "1",
            }
        )
    )
    
dbsubs=["db1","db2"]
dbcidr1=cfg1.require_secret("cidr5")
dbcidr2=cfg1.require_secret("cidr6")
dbcidrs=[dbcidr1,dbcidr2]
for alldbsub in range(len(dbsubs)):
    dbsubs[alldbsub]=aws.ec2.Subnet(
        dbsubs[alldbsub],
        aws.ec2.SubnetArgs(
            vpc_id=vpc1.id,
            cidr_block=dbcidrs[alldbsub],
            availability_zone=zones[alldbsub],
            tags={
                "Name" : dbsubs[alldbsub],
            }
        )
    )   
    
publictable=aws.ec2.RouteTable(
        "publictable",
        aws.ec2.RouteTableArgs(
            vpc_id=vpc1.id,
            routes=[
                aws.ec2.RouteTableRouteArgs(
                    cidr_block=cfg1.require_secret(key="any-traffic-ipv4"),
                    gateway_id=intgw1.id,
                ),
            ],
            tags={
                "Name": "publictable",
            },
        )
    )

tblink1=aws.ec2.RouteTableAssociation(
        "tblink1",
        aws.ec2.RouteTableAssociationArgs(
            subnet_id=pbsubs[0].id,
            route_table_id=publictable.id,
        )
    )

tblink2=aws.ec2.RouteTableAssociation(
        "tblink2",
        aws.ec2.RouteTableAssociationArgs(
            subnet_id=pbsubs[1].id,
            route_table_id=publictable.id,
        )
    )
    
eips=["eip1", "eip2"]
for alleip in range(len(eips)):
    eips[alleip]=aws.ec2.Eip(
        eips[alleip],
        aws.ec2.EipArgs(
            domain="vpc",
            tags={
                "Name": eips[alleip],
            },
        )
    )

natgws=["natgw1", "natgw2"]
allocates=[eips[0].id , eips[1].id]
for allnat in range(len(natgws)):
    natgws[allnat]=aws.ec2.NatGateway(
        natgws[allnat],
        aws.ec2.NatGatewayArgs(
            subnet_id=pbsubs[allpbsub].id,
            allocation_id=allocates[allnat],
            tags={
                "Name": natgws[allnat],
            },
        )
    )

nat_ids=[natgws[0].id , natgws[1].id]  
private_tables=["privatetable1" , "privatetable2"]
for alltables in range(len(private_tables)):
    private_tables[alltables]=aws.ec2.RouteTable(
        private_tables[alltables],
        aws.ec2.RouteTableArgs(
            vpc_id=vpc1.id,
            routes=[
              aws.ec2.RouteTableRouteArgs(
                  cidr_block=cfg1.require_secret(key="any-traffic-ipv4"),
                  nat_gateway_id=nat_ids[alltables]
                  ),
            ],
            tags={
                "Name": private_tables[alltables],
            },
        )
    )

table2link=aws.ec2.RouteTableAssociation(
        "table2link",
        aws.ec2.RouteTableAssociationArgs(
            subnet_id=ndsubs[0].id,
            route_table_id=private_tables[0].id,
        )
    )

table3link=aws.ec2.RouteTableAssociation(
        "table3link",
        aws.ec2.RouteTableAssociationArgs(
            subnet_id=ndsubs[1].id,
            route_table_id=private_tables[1].id,
        )
    )



table5link=aws.ec2.RouteTableAssociation(
        "table5link",
        aws.ec2.RouteTableAssociationArgs(
            subnet_id=dbsubs[0].id,
            route_table_id=private_tables[0].id,
        )
    )

table6link=aws.ec2.RouteTableAssociation(
        "table6link",
        aws.ec2.RouteTableAssociationArgs(
            subnet_id=dbsubs[1].id,
            route_table_id=private_tables[1].id,
        )
    )

inbound_traffic=[
    aws.ec2.NetworkAclIngressArgs(
        from_port=22,
        to_port=22,
        rule_no=100,
        action="deny",
        protocol="tcp",
        cidr_block=cfg1.require_secret(key="any-traffic-ipv4"),
        icmp_code=0,
        icmp_type=0
        ),
    aws.ec2.NetworkAclIngressArgs(
        from_port=22,
        to_port=22,
        rule_no=101,
        action="allow",
        protocol="tcp",
        cidr_block=cfg1.require_secret(key="myips"),
        icmp_code=0,
        icmp_type=0
        ),
    aws.ec2.NetworkAclIngressArgs(
        from_port=80,
        to_port=80,
        rule_no=200,
        action="allow",
        protocol="tcp",
        cidr_block=cfg1.require_secret(key="any-traffic-ipv4"),
        icmp_code=0,
        icmp_type=0
        ),
    aws.ec2.NetworkAclIngressArgs(
        from_port=443,
        to_port=443,
        rule_no=300,
        action="allow",
        protocol="tcp",
        cidr_block=cfg1.require_secret(key="any-traffic-ipv4"),
        icmp_code=0,
        icmp_type=0
        ),
    
 aws.ec2.NetworkAclIngressArgs(
        from_port=1024,
        to_port=65535,
        rule_no=400,
        action="allow",
        protocol="tcp",
        cidr_block=cfg1.require_secret(key="any-traffic-ipv4"),
        icmp_code=0,
        icmp_type=0
        ),
 
    aws.ec2.NetworkAclIngressArgs(
        from_port=0,
        to_port=0,
        rule_no=500,
        action="allow",
        protocol="-1",
        cidr_block=cfg1.require_secret(key="any-traffic-ipv4"),
        icmp_code=0,
        icmp_type=0
        ),
    
]

outbound_traffic=[
        aws.ec2.NetworkAclEgressArgs(
        from_port=22,
        to_port=22,
        rule_no=100,
        action="deny",
        protocol="tcp",
        cidr_block=cfg1.require_secret(key="any-traffic-ipv4"),
        icmp_code=0,
        icmp_type=0
        ),
    aws.ec2.NetworkAclEgressArgs(
        from_port=22,
        to_port=22,
        rule_no=101,
        action="allow",
        protocol="tcp",
        cidr_block=cfg1.require_secret(key="myips"),
        icmp_code=0,
        icmp_type=0
        ),
    aws.ec2.NetworkAclEgressArgs(
        from_port=80,
        to_port=80,
        rule_no=200,
        action="allow",
        protocol="tcp",
        cidr_block=cfg1.require_secret(key="any-traffic-ipv4"),
        icmp_code=0,
        icmp_type=0
        ),
    aws.ec2.NetworkAclEgressArgs(
        from_port=443,
        to_port=443,
        rule_no=300,
        action="allow",
        protocol="tcp",
        cidr_block=cfg1.require_secret(key="any-traffic-ipv4"),
        icmp_code=0,
        icmp_type=0
        ),
    
 aws.ec2.NetworkAclEgressArgs(
        from_port=1024,
        to_port=65535,
        rule_no=400,
        action="allow",
        protocol="tcp",
        cidr_block=cfg1.require_secret(key="any-traffic-ipv4"),
        icmp_code=0,
        icmp_type=0
        ),
 
    aws.ec2.NetworkAclEgressArgs(
        from_port=0,
        to_port=0,
        rule_no=500,
        action="allow",
        protocol="-1",
        cidr_block=cfg1.require_secret(key="any-traffic-ipv4"),
        icmp_code=0,
        icmp_type=0
        ),
]


nacllists=["mynacls1" , "mynacls2"]
for allnacls in range(len(nacllists)):
    nacllists[allnacls]=aws.ec2.NetworkAcl(
        nacllists[allnacls],
        aws.ec2.NetworkAclArgs(
            vpc_id=vpc1.id,
            ingress=inbound_traffic,
            egress=outbound_traffic,
            tags={
                "Name": nacllists[allnacls],
            }
        )
    )
    
    
nacls30=aws.ec2.NetworkAclAssociation(
        "nacls30",
        aws.ec2.NetworkAclAssociationArgs(
            network_acl_id=nacllists[0].id,
            subnet_id=pbsubs[0].id
        )
    )
nacls31=aws.ec2.NetworkAclAssociation(
        "nacls31",
        aws.ec2.NetworkAclAssociationArgs(
            network_acl_id=nacllists[0].id,
            subnet_id=pbsubs[1].id
        )
    )   

nacls10=aws.ec2.NetworkAclAssociation(
        "nacls10",
        aws.ec2.NetworkAclAssociationArgs(
            network_acl_id=nacllists[1].id,
            subnet_id=ndsubs[0].id
        )
    )
nacls11=aws.ec2.NetworkAclAssociation(
        "nacls11",
        aws.ec2.NetworkAclAssociationArgs(
            network_acl_id=nacllists[1].id,
            subnet_id=ndsubs[1].id
        )
    )   

nacls20=aws.ec2.NetworkAclAssociation(
        "nacls20",
        aws.ec2.NetworkAclAssociationArgs(
            network_acl_id=nacllists[1].id,
            subnet_id=dbsubs[0].id
        )
    )
nacls21=aws.ec2.NetworkAclAssociation(
        "nacls21",
        aws.ec2.NetworkAclAssociationArgs(
            network_acl_id=nacllists[1].id,
            subnet_id=dbsubs[1].id
        )
    ) 


eksrole=aws.iam.Role(
    "eksrole",
    aws.iam.RoleArgs(
        assume_role_policy=json.dumps({
            "Version":"2012-10-17",
            "Statement":[
                {
                    "Effect":"Allow",
                    "Principal":{
                        "Service":"eks.amazonaws.com"
                    },
                    "Action": [
                         "sts:AssumeRole",
                         "sts:TagSession",
                         
                        ]
                }
            ]
        })    
))
    

nodesrole=aws.iam.Role(
    "nodesrole",
    aws.iam.RoleArgs(
        assume_role_policy=json.dumps({
            "Version": "2012-10-17",
            "Statement":[
                {
                    "Effect": "Allow",
                    "Principal":{
                        "Service":"ec2.amazonaws.com"
                    },
                 
                    "Action": "sts:AssumeRole"
                }   
            ]
        })
))

clusterattach1=aws.iam.RolePolicyAttachment(
        "clusterattach1",
        aws.iam.RolePolicyAttachmentArgs(
            role=eksrole.name,
            policy_arn="arn:aws:iam::aws:policy/AmazonEKSClusterPolicy",
          
        )
    )

clusterattach2=aws.iam.RolePolicyAttachment(
        "clusterattach2",
        aws.iam.RolePolicyAttachmentArgs(
            role=eksrole.name,
            policy_arn="arn:aws:iam::aws:policy/AmazonEKSComputePolicy",
        )
    )

clusterattach3=aws.iam.RolePolicyAttachment(
        "clusterattach3",
        aws.iam.RolePolicyAttachmentArgs(
            role=eksrole.name,
            policy_arn="arn:aws:iam::aws:policy/AmazonEKSBlockStoragePolicy",
        )
    )

clusterattach4=aws.iam.RolePolicyAttachment(
        "clusterattach4",
        aws.iam.RolePolicyAttachmentArgs(
            role=eksrole.name,
            policy_arn="arn:aws:iam::aws:policy/AmazonEKSLoadBalancingPolicy",
        )
    )


clusterattach5=aws.iam.RolePolicyAttachment(
        "clusterattach5",
        aws.iam.RolePolicyAttachmentArgs(
            role=eksrole.name,
            policy_arn="arn:aws:iam::aws:policy/AmazonEKSNetworkingPolicy",
        )
    )


nodesattach1=aws.iam.RolePolicyAttachment(
        "nodesattach1",
        aws.iam.RolePolicyAttachmentArgs(
            role=nodesrole.name,
            policy_arn="arn:aws:iam::aws:policy/AmazonEKSWorkerNodeMinimalPolicy",
        )
    )

nodesattach2=aws.iam.RolePolicyAttachment(
        "nodesattach2",
        aws.iam.RolePolicyAttachmentArgs(
            role=nodesrole.name,
            policy_arn="arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryPullOnly",
        )
    )


cluster1=aws.eks.Cluster(
    "cluster1",
    aws.eks.ClusterArgs(
        name="cluster1",
        bootstrap_self_managed_addons=False,
        role_arn=eksrole.arn,
        version="1.31",
        compute_config={
          "enabled": True,
          "node_pools": ["general-purpose"],
          "node_role_arn": nodesrole.arn,
        },
        access_config={
         "authentication_mode": "API_AND_CONFIG_MAP",
        },
        storage_config={
           "block_storage": {
            "enabled": True,
        },     
          },
        kubernetes_network_config={
            "elastic_load_balancing": {
            "enabled": True,
            },
        },
        tags={
          "Name" : "cluster1"    
        },
        vpc_config={
        "endpoint_private_access": False,
        "endpoint_public_access": True,
        "public_access_cidrs": [
            cfg1.require_secret(key="myips"),
        ],
        "subnet_ids": [
            ndsubs[0].id,
            ndsubs[1].id,
            pbsubs[0].id,
            pbsubs[1].id,
        ],}
    ),
    opts=pulumi.ResourceOptions(
            depends_on=[
              clusterattach1,
              clusterattach2,
              clusterattach3,
              clusterattach4,
              clusterattach5,
            ]
        )
)

myentry1=aws.eks.AccessEntry(
    "myentry1",
     aws.eks.AccessEntryArgs(
        cluster_name=cluster1.name,
        principal_arn=cfg1.require_secret(key="principal"),
        type="STANDARD"
     ),
     opts=pulumi.ResourceOptions(
            depends_on=[
              cluster1
            ]
        )
)

entrypolicy1=aws.eks.AccessPolicyAssociation(
    "entrypolicy1",
    aws.eks.AccessPolicyAssociationArgs(
        cluster_name=cluster1.name,
        principal_arn=myentry1.principal_arn,
        policy_arn="arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy",
        access_scope={
            "type" : "cluster",
        }
    ),
    opts=pulumi.ResourceOptions(
            depends_on=[
              cluster1
            ]
        )
)


dbsecurity=aws.ec2.SecurityGroup(
    "dbsecurity",
    aws.ec2.SecurityGroupArgs(
        name="dbsecurity",
        description="Security group for database",
        vpc_id=vpc1.id,
        ingress=[
            aws.ec2.SecurityGroupIngressArgs(
                from_port=3306,
                to_port=3306,
                protocol="tcp",
                security_groups=[
                    cluster1.vpc_config.apply( lambda id : id.get(key="cluster_security_group_id"))
                ],
                description="Allow  MySQL Inbound traffic",
            ),
        ],
        egress=[
            aws.ec2.SecurityGroupEgressArgs(
                from_port=0,
                to_port=0,
                protocol="-1",
                cidr_blocks=[
                    cfg1.require_secret(key="any-traffic-ipv4"),
                ],
                description="Allow all outbound traffic",
            )
        ],
        tags={
            "Name": "dbsecurity",
        }
    ),
    opts=pulumi.ResourceOptions(
            depends_on=[
             cluster1            
            ]
        )
)

dbsubnetgrps=aws.rds.SubnetGroup(
    "dbsubnetgrps",
    aws.rds.SubnetGroupArgs(
        name="dbsubnetgrps",
        subnet_ids=[
            dbsubs[0].id,
            dbsubs[1].id,
        ],
        tags={
            "Name": "dbsubnetgrps",
        }
    )
)

dbase=aws.rds.Instance(
    "dbase",
    aws.rds.InstanceArgs(
        db_name="dbaselab",
        engine="mysql",
        engine_version="8.0",
        instance_class="db.t3.micro",
        allocated_storage=20,
        max_allocated_storage=40,
        username=cfg1.require_secret(key="dbuser"),
        password=cfg1.require_secret(key="dbpass"),
        skip_final_snapshot=True,
        delete_automated_backups=True,
        deletion_protection=False,
        allow_major_version_upgrade=True,
        auto_minor_version_upgrade=True,
        publicly_accessible=False,
        apply_immediately=True,
        maintenance_window="Mon:00:00-Mon:03:00",
        backup_window="03:00-06:00",
        backup_retention_period=0,
        db_subnet_group_name=dbsubnetgrps.name,
        vpc_security_group_ids=[dbsecurity.id],
        storage_type="gp3",
        storage_encrypted=False,
        tags={
            "Name": "mydbase",
        },
        multi_az=True
    ),
    opts=pulumi.ResourceOptions(
            depends_on=[
              dbsecurity
            ]
        )
)


pulumi.export("dbendpoint" , value=dbase.endpoint)
pulumi.export("dbname", value=dbase.db_name)
pulumi.export("cluster", value=cluster1.id)