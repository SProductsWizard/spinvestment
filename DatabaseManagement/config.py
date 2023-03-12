FinsightNIURL = {
    "RMBS": r"https://finsight.com/bond-screener/asset-backed-securities?products=ABS&regions=USOA&hash=bbaef5c56e58ef70b20e8f39b375524af0c12e05",
    "ABS": r"https://finsight.com/bond-screener/asset-backed-securities?products=ABS&regions=USOA&hash=7d990255043797f4064152270a1040ac033ea6de",
    "ABSDeal": r"https://finsight.com/abs-exclos-cmbs-rmbs-market-bond-issuance-overview?products=ABS&regions=USOA",
}

DBConfigDict = {
    "Atlas": {
        "user": "user2",  # enter your own user name
        "password": "j8eqXWPwskf0uNoO",  # enter your own user name
        "database": "HF_SP",
        "userReadonly": "user_readonly",
        "passwordReadonly": "qpG4qYs6JImwyRmc",
    },
}

DBConfigDict["Atlas"]["endpoint"] = (
    f"mongodb+srv://{DBConfigDict['Atlas']['user']}:{DBConfigDict['Atlas']['password']}@cluster0.1yhkhhb.mongodb.net",
)

DBConfigDict["Atlas"]["endpointReadonly"] = (
    f"mongodb+srv://{DBConfigDict['Atlas']['userReadonly']}:{DBConfigDict['Atlas']['passwordReadonly']}@cluster0.1yhkhhb.mongodb.net",
)


HrefSubassetClassDict = {
    "https://finsight.com/auto-floorplan-abs-bond-issuance-overview?products=ABS&regions=USOA": "floorPlan",
    "https://finsight.com/auto-lease-abs-bond-issuance-overview?products=ABS&regions=USOA": "autoLease",
    "https://finsight.com/auto-motorcycle-abs-bond-issuance-overview?products=ABS&regions=USOA": "motorcycle",
    "https://finsight.com/auto-prime-loan-abs-bond-issuance-overview?products=ABS&regions=USOA": "primeAuto",
    "https://finsight.com/auto-subprime-loan-abs-bond-issuance-overview?products=ABS&regions=USOA": "subprimeAuto",
    "https://finsight.com/credit-card-bank-charge-card-abs-bond-issuance-overview?products=ABS&regions=USOA": "bankCard",
    "https://finsight.com/credit-card-retail-private-label-abs-bond-issuance-overview?products=ABS&regions=USOA": "privateCard",
    "https://finsight.com/equipment-agri-construction-abs-bond-issuance-overview?products=ABS&regions=USOA": "equipAgriConstruction",
    "https://finsight.com/equipment-floorplan-abs-bond-issuance-overview?products=ABS&regions=USOA": "equipFloorPlan",
    "https://finsight.com/equipment-large-ticket-abs-bond-issuance-overview?products=ABS&regions=USOA": "equipLargeTicket",
    "https://finsight.com/equipment-small-mid-ticket-abs-bond-issuance-overview?products=ABS&regions=USOA": "equipSmallMidTicket",
    "https://finsight.com/student-loan-ffelp-abs-bond-issuance-overview?products=ABS&regions=USOA": "FFELP",
    "https://finsight.com/student-loan-private-abs-bond-issuance-overview?products=ABS&regions=USOA": "privateSL",
    "https://finsight.com/esoteric-aircraft-receivables-abs-bond-issuance-overview?products=ABS&regions=USOA": "aircraft",
    "https://finsight.com/esoteric-cell-tower-datacenter-billboard-abs-bond-issuance-overview?products=ABS&regions=USOA": "cellTowerDatacenterBillboard",
    "https://finsight.com/esoteric-consumer-marketplace-loans-abs-bond-issuance-overview?products=ABS&regions=USOA": "consumerLoan",
    "https://finsight.com/esoteric-container-abs-bond-issuance-overview?products=ABS&regions=USOA": "container",
    "https://finsight.com/esoteric-device-payment-plans-abs-bond-issuance-overview?products=ABS&regions=USOA": "devicePayment",
    "https://finsight.com/esoteric-fleet-lease-abs-bond-issuance-overview?products=ABS&regions=USOA": "fleetLease",
    "https://finsight.com/esoteric-insurance-premium-finance-other-abs-bond-issuance-overview?products=ABS&regions=USOA": "insurancePremium",
    "https://finsight.com/esoteric-insurance-structured-settlements-abs-bond-issuance-overview?products=ABS&regions=USOA": "insuranceStructuredSettlement",
    "https://finsight.com/esoteric-ip-royalties-abs-bond-issuance-overview?products=ABS&regions=USOA": "ipRoyalties",
    "https://finsight.com/esoteric-municipal-pace-bonds-abs-bond-issuance-overview?products=ABS&regions=USOA": "PACE",
    "https://finsight.com/esoteric-railcar-abs-bond-issuance-overview?products=ABS&regions=USOA": "railcar",
    "https://finsight.com/esoteric-rate-reduction-bonds-abs-bond-issuance-overview?products=ABS&regions=USOA": "rateReduction",
    "https://finsight.com/esoteric-rental-car-abs-bond-issuance-overview?products=ABS&regions=USOA": "rentalCar",
    "https://finsight.com/esoteric-small-business-loans-abs-bond-issuance-overview?products=ABS&regions=USOA": "smallBiz",
    "https://finsight.com/esoteric-solar-abs-bond-issuance-overview?products=ABS&regions=USOA": "solar",
    "https://finsight.com/esoteric-specialty-finance-other-abs-bond-issuance-overview?products=ABS&regions=USOA": "speciltyFinance",
    "https://finsight.com/esoteric-tax-liens-abs-bond-issuance-overview?products=ABS&regions=USOA": "taxLien",
    "https://finsight.com/esoteric-timeshare-abs-bond-issuance-overview?products=ABS&regions=USOA": "timeshare",
    "https://finsight.com/esoteric-triple-net-lease-abs-bond-issuance-overview?products=ABS&regions=USOA": "tripleNetLease",
    "https://finsight.com/esoteric-whole-business-abs-bond-issuance-overview?products=ABS&regions=USOA": "wholeBiz",
}
