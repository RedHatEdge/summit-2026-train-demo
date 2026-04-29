# Must be logged into flightctl cli

# Create Catalog
flightctl apply -f catalog.yaml

# Create Catalog Items
flightctl apply -f app.yaml
flightctl apply -f os.yaml
flightctl apply -f edge.yaml

