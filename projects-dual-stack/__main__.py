"""An AWS Python Pulumi program"""
import pulumi , json  , pulumi_aws  as aws

mycfg=pulumi.Config()

vpc1ipv6=aws.ec2.Vpc(
    "vpc1ipv6",
    aws.ec2.VpcArgs(
     cidr_block="88.132.0.0/16",
     assign_generated_ipv6_cidr_block=True,
     tags={
         "Name": "vpc1ipv6",
     }
    )
)

myipv6cidr=vpc1ipv6.ipv6_cidr_block
pulumi.export("ipv6cidrs" , value=myipv6cidr)
blockipv61=[ "01::/76" , "02::/76" ]
blockipv62=[ "03::/76","04::/76" ]
blockipv63=[ "05::/76","06::/76" ]

subnetsname1=["sub1" , "sub2"]
subnetsname2=["sub3" , "sub4"]
subnetsname3=["sub5" , "sub6"]
subnet1=myipv6cidr.apply(lambda changes: changes.replace(mycfg.require_secret(key="change-ranges"), blockipv61[0]))
subnet2=myipv6cidr.apply(lambda changes: changes.replace(mycfg.require_secret(key="change-ranges"), blockipv61[1]))
subnet3=myipv6cidr.apply(lambda changes: changes.replace(mycfg.require_secret(key="change-ranges"), blockipv62[0]))
subnet4=myipv6cidr.apply(lambda changes: changes.replace(mycfg.require_secret(key="change-ranges"), blockipv62[1]))
subnet5=myipv6cidr.apply(lambda changes: changes.replace(mycfg.require_secret(key="change-ranges"), blockipv63[0]))
subnet6=myipv6cidr.apply(lambda changes: changes.replace(mycfg.require_secret(key="change-ranges"), blockipv63[1]))
cidrlists1=[subnet1 , subnet2 ]
cidrlists2=[subnet3 , subnet4 ]
cidrlists3=[subnet5 , subnet6 ]
pulumi.export("cidrs1" , value=cidrlists1)
pulumi.export("cidrs2", value=cidrlists2)
pulumi.export("cidrs3", value=cidrlists3)
zoneslist=[ "us-east-1a" , "us-east-1b"]
ipv4block1=["88.132.100.0/24" , "88.132.101.0/24"]
ipv4block2=["88.132.102.0/24" , "88.132.103.0/24"]
ipv4block3=["88.132.104.0/24" , "88.132.105.0/24"]


for allsubs1 in range(len(subnetsname1)):
    subnetsname1[allsubs1]=aws.ec2.Subnet(
        subnetsname1[allsubs1],
        aws.ec2.SubnetArgs(
            cidr_block=ipv4block1[allsubs1],
            ipv6_cidr_block=cidrlists1[allsubs1],
            vpc_id=vpc1ipv6.id,
            availability_zone=zoneslist[allsubs1],
            tags={
                "Name": subnetsname1[allsubs1],
            }
        )
    )
    
for allsubs2 in range(len(subnetsname2)):
    subnetsname2[allsubs2]=aws.ec2.Subnet(
        subnetsname2[allsubs2],
        aws.ec2.SubnetArgs(
            cidr_block=ipv4block2[allsubs2],
            ipv6_cidr_block=cidrlists2[allsubs2],
            vpc_id=vpc1ipv6.id,
            availability_zone=zoneslist[allsubs2],
            tags={
                "Name": subnetsname2[allsubs2],
            },
        )
    )    
    
for allsubs3 in range(len(subnetsname3)):
    subnetsname3[allsubs3]=aws.ec2.Subnet(
        subnetsname3[allsubs3],
        aws.ec2.SubnetArgs(
            cidr_block=ipv4block3[allsubs3],
            ipv6_cidr_block=cidrlists3[allsubs3],
            vpc_id=vpc1ipv6.id,
            availability_zone=zoneslist[allsubs3],
            tags={
                "Name": subnetsname3[allsubs3],
            },
        )
    )     
    

    
eigw=aws.ec2.EgressOnlyInternetGateway()

intgw=aws.ec2.InternetGateway(
    "intgw",
    aws.ec2.InternetGatewayArgs(
        vpc_id=vpc1ipv6.id,
        tags={
            "Name": "intgw",
        }
    )
)

table1=aws.ec2.RouteTable(
    "table1",
    aws.ec2.RouteTableArgs(
         vpc_id=vpc1ipv6.id,
         tags={
             "Name": "table1",
         },
         routes=[
             aws.ec2.RouteTableRouteArgs(
                 cidr_block=mycfg.require_secret(key="any-traffic-ipv4"),
                 gateway_id=intgw.id
             ),
             aws.ec2.RouteTableRouteArgs(
                 ipv6_cidr_block=mycfg.require_secret(key="any-traffic-ipv6"),
                 gateway_id=intgw.id,
             )
         ]
        
    )
)

table2=aws.ec2.RouteTable(
    "table2",
    aws.ec2.RouteTableArgs(
         vpc_id=vpc1ipv6.id,
         tags={
             "Name": "table2",
         },
         routes=[
             aws.ec2.RouteTableRouteArgs(
                 ipv6_cidr_block="::/0",
                 gateway_id=eigw.id,
             )
         ]
    )
)


associates_table1=["tablelink1" , "tablelink2"]
for all_associates in range(len(associates_table1)):
    associates_table1[all_associates]=aws.ec2.RouteTableAssociation(
        associates_table1[all_associates] ,
        aws.ec2.RouteTableAssociationArgs(
               route_table_id=table1.id,
               subnet_id=subnetsname2[allsubs1]
        ) 
    )

associates_table2=["tablelink3" , "tablelink4"]
for all_associates2 in range(len(associates_table2)):
    associates_table2[all_associates2]=aws.ec2.RouteTableAssociation(
        associates_table2[all_associates2] ,
        aws.ec2.RouteTableAssociationArgs(
               route_table_id=table2.id,
               subnet_id=subnetsname2[allsubs2]
        ) 
    )


associates_table3=["tablelink5" , "tablelink6"]
for all_associates3 in range(len(associates_table3)):
    associates_table3[all_associates3]=aws.ec2.RouteTableAssociation(
        associates_table3[all_associates3] ,
        aws.ec2.RouteTableAssociationArgs(
               route_table_id=table2.id,
               subnet_id=subnetsname3[allsubs3]
        ) 
    )

    

lbsecurity=aws.ec2.SecurityGroup()

websecurity=aws.ec2.SecurityGroup()

dbsecurity=aws.ec2.SecurityGroup()