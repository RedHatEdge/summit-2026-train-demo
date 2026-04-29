1. Create inference-v#.container files to be used by scratch container

v1:
[Unit]
Description=Inference(Edge AI train control)
After=network-online.target
Wants=network-online.target
[Container]
Image=quay.io/kenosborn/inference-train-demo:v1
AddDevice=/dev/video0
AddDevice=/dev/video1
PublishPort=8080:8080
Environment=CAM_W=640
Environment=CAM_H=480
Environment=DISPLAY_SIZE=800
Environment=ARM_THRESHOLD=0.85
Environment=MARGIN_MIN=0.50
Environment=STABLE_FRAMES=6
Environment=COOLDOWN_SEC=3.0
Environment=MQTT_ENABLED=false
Environment=MQTT_BROKER=10.20.0.150
Environment=MQTT_PORT=1883
Environment=MQTT_TOPIC=train/cmd
SecurityLabelDisable=true
User=root
[Install]
WantedBy=default.target

v2:
[Unit]
Description=Inference(Edge AI train control)
After=network-online.target
Wants=network-online.target
[Container]
Image=quay.io/kenosborn/inference-train-demo:v2
AddDevice=/dev/video0
AddDevice=/dev/video1
PublishPort=8080:8080
Environment=CAM_W=640
Environment=CAM_H=480
Environment=DISPLAY_SIZE=800
Environment=ARM_THRESHOLD=0.85
Environment=MARGIN_MIN=0.50
Environment=STABLE_FRAMES=6
Environment=COOLDOWN_SEC=3.0
Environment=MQTT_ENABLED=false
Environment=MQTT_BROKER=10.20.0.150
Environment=MQTT_PORT=1883
Environment=MQTT_TOPIC=train/cmd
SecurityLabelDisable=true
User=root
[Install]
WantedBy=default.target

2. Create and publish scratch containers

v1 scratch Containerfile-v1:
FROM scratch
COPY inference-v1.container /inference.container

v2 scratch Containerfile-v2:
FROM scratch
COPY inference-v2.container /inference.container

podman build --no-cache -t quay.io/kenosborn/ai-inference-app:v1 Containerfile-v1
podman build --no-cache -t quay.io/kenosborn-ai-inference-app:v2 Containerfile-v2

3. Create Catalog Item (app-inference.yaml):
apiVersion: flightctl.io/v1alpha1
kind: CatalogItem
metadata:
  name: inference-train-demo
  catalog: edge-ai-apps

spec:
  type: quadlet
  displayName: Inference (Edge AI Train Control)
  shortDescription: Edge AI inference app for train demo with camera input
  artifacts:
    - type: container
      uri: quay.io/kenosborn/inference-app
  versions:
    - version: "3.0.0"
      references:
        container: "v3"
      channels:
        - fast
      replaces: "2.0.0"
      readme: |
        ## Inference Train Demo 3.0.0 (Fast)
        Preview release with next-generation inference improvements and experimental features.
    - version: "2.0.0"
      references:
        container: "v2"
      channels:
        - stable
      replaces: "1.0.0"
      readme: |
        ## Inference Train Demo 2.0.0 (Stable)
        Stable release with enhanced dashboard capability.
    - version: "1.0.0"
      references:
        container: "v1"
      channels:
        - stable
      readme: |
        ## Inference Train Demo 1.0.0 (Stable)
        Initial stable release of the edge AI inference application for train control.
  defaults:
    config:
      envVars:
        CAM_W: "640"
        CAM_H: "480"
        DISPLAY_SIZE: "800"
        USE_PAPER_GATE: "false"
        ARM_THRESHOLD: "0.85"
        MARGIN_MIN: "0.50"
        STABLE_FRAMES: "6"
        COOLDOWN_SEC: "3.0"
        MQTT_ENABLED: "false"
        MQTT_BROKER: "10.20.0.150"
        MQTT_PORT: "1883"
        MQTT_TOPIC: "train/cmd"

4. Create Catalog yaml for "Edge AI Apps" (edge-ai-apps-catalog.yaml)
apiVersion: flightctl.io/v1alpha1
kind: Catalog
metadata:
  name: edge-ai-apps
  labels:
    environment: production
spec:
  displayName: Edge AI Apps
  provider: Platform Team
  support: https://wiki.acme.com/edge-ai-apps
  visibility: published

5. Create Catalog Item for Inference App ("inference-app.yaml") (IP Address must be updated to show MQ IP address)
apiVersion: flightctl.io/v1alpha1
kind: CatalogItem
metadata:
  name: inference-train-demo
  catalog: edge-ai-apps

spec:
  type: quadlet
  displayName: Inference (Edge AI Train Control)
  shortDescription: Edge AI inference app for train demo with camera input
  artifacts:
    - type: container
      uri: quay.io/kenosborn/inference-app
  versions:
    - version: "3.0.0"
      references:
        container: "v3"
      channels:
        - fast
      replaces: "2.0.0"
      readme: |
        ## Inference Train Demo 3.0.0 (Fast)
        Preview release with next-generation inference improvements and experimental features.
    - version: "2.0.0"
      references:
        container: "v2"
      channels:
        - stable
      replaces: "1.0.0"
      readme: |
        ## Inference Train Demo 2.0.0 (Stable)
        Stable release with enhanced dashboard capability.
    - version: "1.0.0"
      references:
        container: "v1"
      channels:
        - stable
      readme: |
        ## Inference Train Demo 1.0.0 (Stable)
        Initial stable release of the edge AI inference application for train control.
  defaults:
    config:
      envVars:
        CAM_W: "640"
        CAM_H: "480"
        DISPLAY_SIZE: "800"
        USE_PAPER_GATE: "false"
        ARM_THRESHOLD: "0.85"
        MARGIN_MIN: "0.50"
        STABLE_FRAMES: "6"
        COOLDOWN_SEC: "3.0"
        MQTT_ENABLED: "false"
        MQTT_BROKER: "10.20.0.150"
        MQTT_PORT: "1883"
        MQTT_TOPIC: "train/cmd"

6. Apply Catalog and Catalog Item using flightctl cli

flightctl apply -f edge-ai-apps-catalog.yaml
flightctl apply -f inference-app.yaml


