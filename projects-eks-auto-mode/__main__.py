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
                "Name": pbsubs[allpbsub],
                "kubernetes.io/role/elb": "1",
                "kubernetes.io/cluster/myclusters" : "owned"
            }
        )
    )

ndsubs=["node1","node2"]
zones=["us-east-1a","us-east-1b"]
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
                "Name": ndsubs[allndsub],
                "kubernetes.io/role/internal-elb": "1",
                "kubernetes.io/cluster/myclusters" : "owned"
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

natgws=["nat1", "nat2"]
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

mynacls=aws.ec2.NetworkAcl(
    "mynacls",
    aws.ec2.NetworkAclArgs(
        vpc_id=vpc1.id,
        ingress=[
           aws.ec2.NetworkAclIngressArgs(
               from_port=22,
               to_port=22,
               protocol="tcp", 
               cidr_block=cfg1.require_secret(key="any-traffic-ipv4"),
               icmp_code=0,
               icmp_type=0,
               action="deny",
               rule_no=100
               ),
           aws.ec2.NetworkAclIngressArgs(
               from_port=22,
               to_port=22,
               protocol="tcp", 
               cidr_block=cfg1.require_secret(key="myips"),
               icmp_code=0,
               icmp_type=0,
               action="allow",
               rule_no=101
               ),
           aws.ec2.NetworkAclIngressArgs(
               from_port=80,
               to_port=80,
               protocol="tcp", 
               cidr_block=cfg1.require_secret(key="any-traffic-ipv4"),
               icmp_code=0,
               icmp_type=0,
               action="allow",
               rule_no=200
               ),
           aws.ec2.NetworkAclIngressArgs(
               from_port=443,
               to_port=443,
               protocol="tcp", 
               cidr_block=cfg1.require_secret(key="any-traffic-ipv4"),
               icmp_code=0,
               icmp_type=0,
               action="allow",
               rule_no=300
               ),
            aws.ec2.NetworkAclIngressArgs(
               from_port=1024,
               to_port=65535,
               protocol="tcp", 
               cidr_block=cfg1.require_secret(key="any-traffic-ipv4"),
               icmp_code=0,
               icmp_type=0,
               action="allow",
               rule_no=400
               ),  
           aws.ec2.NetworkAclIngressArgs(
               from_port=0,
               to_port=0,
               protocol="-1", 
               cidr_block=cfg1.require_secret(key="any-traffic-ipv4"),
               icmp_code=0,
               icmp_type=0,
               action="allow",
               rule_no=500
               ),
            ],
        egress=[
            aws.ec2.NetworkAclEgressArgs(
               from_port=22,
               to_port=22,
               protocol="tcp", 
               cidr_block=cfg1.require_secret(key="any-traffic-ipv4"),
               icmp_code=0,
               icmp_type=0,
               action="deny",
               rule_no=100
                ),
            aws.ec2.NetworkAclEgressArgs(
               from_port=22,
               to_port=22,
               protocol="tcp", 
               cidr_block=cfg1.require_secret(key="myips"),
               icmp_code=0,
               icmp_type=0,
               action="allow",
               rule_no=101
                ),
               aws.ec2.NetworkAclEgressArgs(
               from_port=80,
               to_port=80,
               protocol="tcp", 
               cidr_block=cfg1.require_secret(key="any-traffic-ipv4"),
               icmp_code=0,
               icmp_type=0,
               action="allow",
               rule_no=200
                ),
               aws.ec2.NetworkAclEgressArgs(
               from_port=443,
               to_port=443,
               protocol="tcp", 
               cidr_block=cfg1.require_secret(key="any-traffic-ipv4"),
               icmp_code=0,
               icmp_type=0,
               action="allow",
               rule_no=300
                ),
               aws.ec2.NetworkAclEgressArgs(
               from_port=1024,
               to_port=65535,
               protocol="tcp", 
               cidr_block=cfg1.require_secret(key="any-traffic-ipv4"),
               icmp_code=0,
               icmp_type=0,
               action="allow",
               rule_no=400
                ),
               aws.ec2.NetworkAclEgressArgs(
               from_port=0,
               to_port=0,
               protocol="-1", 
               cidr_block=cfg1.require_secret(key="any-traffic-ipv4"),
               icmp_code=0,
               icmp_type=0,
               action="allow",
               rule_no=500
                ),
            ],
        tags={
            "Name": "mynacls",
        }
    )
)

nacls30=aws.ec2.NetworkAclAssociation(
        "nnacls30",
        aws.ec2.NetworkAclAssociationArgs(
            network_acl_id=mynacls.id,
            subnet_id=pbsubs[0].id
        )
    )
nacls31=aws.ec2.NetworkAclAssociation(
        "nnacls31",
        aws.ec2.NetworkAclAssociationArgs(
            network_acl_id=mynacls.id,
            subnet_id=pbsubs[1].id
        )
    )   



nodes_nacls=aws.ec2.NetworkAcl(
    "nodes_nacls",
    aws.ec2.NetworkAclArgs(
        vpc_id=vpc1.id,
        ingress=[
           aws.ec2.NetworkAclIngressArgs(
               from_port=22,
               to_port=22,
               protocol="tcp", 
               cidr_block=cfg1.require_secret(key="any-traffic-ipv4"),
               icmp_code=0,
               icmp_type=0,
               action="deny",
               rule_no=100
               ),
           aws.ec2.NetworkAclIngressArgs(
               from_port=22,
               to_port=22,
               protocol="tcp", 
               cidr_block=cfg1.require_secret(key="myips"),
               icmp_code=0,
               icmp_type=0,
               action="allow",
               rule_no=101
               ),
            aws.ec2.NetworkAclIngressArgs(
               from_port=80,
               to_port=80,
               protocol="tcp", 
               cidr_block=cfg1.require_secret(key="any-traffic-ipv4"),
               icmp_code=0,
               icmp_type=0,
               action="allow",
               rule_no=200
               ),
            aws.ec2.NetworkAclIngressArgs(
               from_port=443,
               to_port=443,
               protocol="tcp",
               cidr_block=cfg1.require_secret(key="any-traffic-ipv4"),
               icmp_code=0,
               icmp_type=0,
               action="allow",
               rule_no=300
               ),
            aws.ec2.NetworkAclIngressArgs(
               from_port=3306,
               to_port=3306,
               protocol="tcp", 
               cidr_block=cfg1.require_secret(key="any-traffic-ipv4"),
               icmp_code=0,
               icmp_type=0,
               action="allow",
               rule_no=400
                ),
            aws.ec2.NetworkAclIngressArgs(
               from_port=1024,
               to_port=65535,
               protocol="tcp", 
               cidr_block=cfg1.require_secret(key="any-traffic-ipv4"),
               icmp_code=0,
               icmp_type=0,
               action="allow",
               rule_no=500
               ),  
           aws.ec2.NetworkAclIngressArgs(
               from_port=0,
               to_port=0,
               protocol="-1", 
               cidr_block=cfg1.require_secret(key="any-traffic-ipv4"),
               icmp_code=0,
               icmp_type=0,
               action="allow",
               rule_no=600
               ),
            ],
        egress=[
            aws.ec2.NetworkAclEgressArgs(
               from_port=22,
               to_port=22,
               protocol="tcp", 
               cidr_block=cfg1.require_secret(key="any-traffic-ipv4"),
               icmp_code=0,
               icmp_type=0,
               action="deny",
               rule_no=100
                ),
            aws.ec2.NetworkAclEgressArgs(
               from_port=22,
               to_port=22,
               protocol="tcp", 
               cidr_block=cfg1.require_secret(key="myips"),
               icmp_code=0,
               icmp_type=0,
               action="allow",
               rule_no=101
                ),
               aws.ec2.NetworkAclEgressArgs(
               from_port=80,
               to_port=80,
               protocol="tcp", 
               cidr_block=cfg1.require_secret(key="any-traffic-ipv4"),
               icmp_code=0,
               icmp_type=0,
               action="allow",
               rule_no=200
                ),
               aws.ec2.NetworkAclEgressArgs(
               from_port=443,
               to_port=443,
               protocol="tcp", 
               cidr_block=cfg1.require_secret(key="any-traffic-ipv4"),
               icmp_code=0,
               icmp_type=0,
               action="allow",
               rule_no=300
                ),
               aws.ec2.NetworkAclEgressArgs(
               from_port=3306,
               to_port=3306,
               protocol="tcp", 
               cidr_block=cfg1.require_secret(key="any-traffic-ipv4"),
               icmp_code=0,
               icmp_type=0,
               action="allow",
               rule_no=400
                ),
               aws.ec2.NetworkAclEgressArgs(
               from_port=1024,
               to_port=65535,
               protocol="tcp", 
               cidr_block=cfg1.require_secret(key="any-traffic-ipv4"),
               icmp_code=0,
               icmp_type=0,
               action="allow",
               rule_no=500
                ),
               aws.ec2.NetworkAclEgressArgs(
               from_port=0,
               to_port=0,
               protocol="-1", 
               cidr_block=cfg1.require_secret(key="any-traffic-ipv4"),
               icmp_code=0,
               icmp_type=0,
               action="allow",
               rule_no=600
                ),
            ],
        tags={
            "Name": "nodes_nacls",
        }
    )
)


nacls10=aws.ec2.NetworkAclAssociation(
        "nacls10",
        aws.ec2.NetworkAclAssociationArgs(
            network_acl_id=nodes_nacls.id,
            subnet_id=ndsubs[0].id
        )
    )
nacls11=aws.ec2.NetworkAclAssociation(
        "nacls11",
        aws.ec2.NetworkAclAssociationArgs(
            network_acl_id=nodes_nacls.id,
            subnet_id=ndsubs[1].id
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


myclusters=aws.eks.Cluster(
    "myclusters",
    aws.eks.ClusterArgs(
        name="myclusters",
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
          "Name" : "myclusters"    
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
        cluster_name=myclusters.name,
        principal_arn=cfg1.require_secret(key="principal"),
        type="STANDARD"
     ),
     opts=pulumi.ResourceOptions(
            depends_on=[
              myclusters
            ]
        )
)

entrypolicy1=aws.eks.AccessPolicyAssociation(
    "entrypolicy1",
    aws.eks.AccessPolicyAssociationArgs(
        cluster_name=myclusters.name,
        principal_arn=myentry1.principal_arn,
        policy_arn="arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy",
        access_scope={
            "type" : "cluster",
        }
    ),
    opts=pulumi.ResourceOptions(
            depends_on=[
              myclusters
            ]
        )
)