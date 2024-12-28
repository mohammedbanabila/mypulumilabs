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
            tags={
                "Name": pbsubs[allpbsub],
                "kubernetes.io/role/elb": "1",
            },
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
            },
        )
    )
    
dbsubs=["db1","db2"]
zones=["us-east-1a","us-east-1b"]
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
                "Name": ndsubs[alldbsub],
            },
        )
    )
    
table1=aws.ec2.RouteTable(
    "table1",
    aws.ec2.RouteTableArgs(
        vpc_id=vpc1.id,
        routes=[
            aws.ec2.RouteTableRouteArgs(
                cidr_block=cfg1.require_secret(key="any-traffic-ipv4"),
                gateway_id=intgw1.id,
            ),
        ],
        tags={
            "Name": "table1",
        },
    )
)

table1_associates=["tblink1" , "tblink2"]
for alltablelist_associate in range(len(table1_associates)):
    table1_associates[alltablelist_associate]=aws.ec2.RouteTableAssociation(
        table1_associates[alltablelist_associate],
        aws.ec2.RouteTableAssociationArgs(
            subnet_id=pbsubs[allpbsub].id,
            route_table_id=table1.id,
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
subnat=[pbsubs[0].id , pbsubs[1].id]
allocates=[eips[0].id , eips[1].id]
for allnat in range(len(natgws)):
    natgws[allnat]=aws.ec2.NatGateway(
        natgws[allnat],
        aws.ec2.NatGatewayArgs(
            subnet_id=subnat[allnat],
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

tables_associates2=[ "table2link","table3link"]
for alltable2 in range(len(tables_associates2)):
    tables_associates2[alltable2]=aws.ec2.RouteTableAssociation(
        tables_associates2[alltable2],
        aws.ec2.RouteTableAssociationArgs(
            subnet_id=ndsubs[allndsub].id,
            route_table_id=private_tables[alltables].id,
        )
    )

tables_associates3=[ "table4link","table5link"]
for alltable3 in range(len(tables_associates3)):
    tables_associates3[alltable3]=aws.ec2.RouteTableAssociation(
        tables_associates3[alltable3],
        aws.ec2.RouteTableAssociationArgs(
            subnet_id=dbsubs[alldbsub].id,
            route_table_id=private_tables[alltables].id,
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
               from_port=5432,
               to_port=5432,
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
               from_port=5432,
               to_port=5432,
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

nacllnk1=["nacl1","nacl2"] 
for allnacllinks1 in range(len(nacllnk1)):
    nacllnk1[allnacllinks1]=aws.ec2.NetworkAclAssociation(
        nacllnk1[allnacllinks1],
        aws.ec2.NetworkAclAssociationArgs(
            network_acl_id=mynacls.id,
            subnet_id=pbsubs[allpbsub].id
        )
    )
    

nacllnk2=["nacl3","nacl4"] 
for allnacllinks2 in range(len(nacllnk2)):
    nacllnk2[allnacllinks2]=aws.ec2.NetworkAclAssociation(
        nacllnk2[allnacllinks2],
        aws.ec2.NetworkAclAssociationArgs(
            network_acl_id=mynacls.id,
            subnet_id=ndsubs[allndsub].id
        )
    )
    

nacllnk3=["nacll5","nacl6"] 
for allnacllinks3 in range(len(nacllnk3)):
    nacllnk3[allnacllinks3]=aws.ec2.NetworkAclAssociation(
        nacllnk3[allnacllinks3],
        aws.ec2.NetworkAclAssociationArgs(
            network_acl_id=mynacls.id,
            subnet_id=dbsubs[alldbsub].id
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
                    "Action": "sts:AssumeRole"
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
                },
            ]
        })
))

cluster_amazon_eks_cluster_policy = aws.iam.RolePolicyAttachment("cluster_AmazonEKSClusterPolicy",
    policy_arn="arn:aws:iam::aws:policy/AmazonEKSClusterPolicy",
    role=eksrole.name)
cluster_amazon_eks_compute_policy = aws.iam.RolePolicyAttachment("cluster_AmazonEKSComputePolicy",
    policy_arn="arn:aws:iam::aws:policy/AmazonEKSComputePolicy",
    role=eksrole.name)
cluster_amazon_eks_block_storage_policy = aws.iam.RolePolicyAttachment("cluster_AmazonEKSBlockStoragePolicy",
    policy_arn="arn:aws:iam::aws:policy/AmazonEKSBlockStoragePolicy",
    role=eksrole.name)
cluster_amazon_eks_load_balancing_policy = aws.iam.RolePolicyAttachment("cluster_AmazonEKSLoadBalancingPolicy",
    policy_arn="arn:aws:iam::aws:policy/AmazonEKSLoadBalancingPolicy",
    role=eksrole.name)
cluster_amazon_eks_networking_policy = aws.iam.RolePolicyAttachment("cluster_AmazonEKSNetworkingPolicy",
    policy_arn="arn:aws:iam::aws:policy/AmazonEKSNetworkingPolicy",
    role=eksrole.name)

node_amazon_eks_worker_node_minimal_policy = aws.iam.RolePolicyAttachment("node_AmazonEKSWorkerNodeMinimalPolicy",
    policy_arn="arn:aws:iam::aws:policy/AmazonEKSWorkerNodeMinimalPolicy",
    role=nodesrole.name)
node_amazon_ec2_container_registry_pull_only = aws.iam.RolePolicyAttachment("node_AmazonEC2ContainerRegistryPullOnly",
    policy_arn="arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryPullOnly",
    role=nodesrole.name)

mycluster=aws.eks.Cluster(
    "mycluster",
    aws.eks.ClusterArgs(
        name="mycluster",
        role_arn=eksrole.arn,
        version="1.30",
        bootstrap_self_managed_addons=False,
        compute_config={
          "enabled": True,
          "node_pools": ["general-purpose"],
          "node_role_arn": nodesrole.arn,
        },
        access_config={
            "authentication_mode": "API",
        },
        kubernetes_network_config={
        "elastic_load_balancing": {
            "enabled": True,
        }},
        storage_config={
           "block_storage": {
            "enabled": True,
        }, 
        },
        tags={
            "Name": "mycluster",
        },
        vpc_config={
            "endpoint_public_access": True,
            "endpoint_private_access": False,
            "public_access_cidrs": [ cfg1.require_secret(key="myips")],
            "subnet_ids": [
                pbsubs[0].id,
                pbsubs[1].id,
                ndsubs[0].id,
                ndsubs[1].id,

            ],
        }),
        opts=pulumi.ResourceOptions(
            depends_on=[
                cluster_amazon_eks_block_storage_policy,
                cluster_amazon_eks_cluster_policy,
                cluster_amazon_eks_load_balancing_policy,
                cluster_amazon_eks_networking_policy,
                cluster_amazon_eks_compute_policy,
                node_amazon_ec2_container_registry_pull_only,
                node_amazon_eks_worker_node_minimal_policy,
            ]
        )
)


cluster_security_rule1 =aws.ec2.SecurityGroupRule(
    "cluster_security_rule1",
    aws.ec2.SecurityGroupRuleArgs(
        from_port=80,
        to_port=80,
        cidr_blocks=[cfg1.require_secret(key="any-traffic-ipv4")],
        protocol="tcp",
        security_group_id=mycluster.vpc_config.apply( lambda id: id.get(key="cluster_security_group_id")),
        type="ingress"
     ),
)


cluster_security_rule2=aws.ec2.SecurityGroupRule(
    "cluster_security_rule2",
    aws.ec2.SecurityGroupRuleArgs(
        from_port=443,
        to_port=443,
        cidr_blocks=[cfg1.require_secret(key="any-traffic-ipv4")],
        protocol="tcp",
        security_group_id=mycluster.vpc_config.apply( lambda id: id.get(key="cluster_security_group_id")),
        type="ingress"
     ),
)

cluster_security_rule3=aws.ec2.SecurityGroupRule(
    "cluster_security_rule3",
    aws.ec2.SecurityGroupRuleArgs(
        from_port=53,
        to_port=53,
        cidr_blocks=[cfg1.require_secret(key="any-traffic-ipv4")],
        protocol="udp",
        security_group_id=mycluster.vpc_config.apply( lambda id: id.get(key="cluster_security_group_id")),
        type="ingress"
     ),
)

cluster_security_rule4=aws.ec2.SecurityGroupRule(
    "cluster_security_rule4",
    aws.ec2.SecurityGroupRuleArgs(
        from_port=5432,
        to_port=5432,
        cidr_blocks=[cfg1.require_secret(key="any-traffic-ipv4")],
        protocol="tcp",
        type="ingress",
        security_group_id=mycluster.vpc_config.apply( lambda id: id.get(key="cluster_security_group_id"))
     ),
)
cluster_security_rule5=aws.ec2.SecurityGroupRule(
    "cluster_security_rule5",
    aws.ec2.SecurityGroupRuleArgs(
        from_port=10249,
        to_port=10249,
        cidr_blocks=[cfg1.require_secret(key="any-traffic-ipv4")],
        protocol="tcp",
        type="ingress",
        security_group_id=mycluster.vpc_config.apply( lambda id: id.get(key="cluster_security_group_id"))
     ),
)