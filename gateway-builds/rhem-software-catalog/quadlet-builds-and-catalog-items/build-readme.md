# Edge AI Inference App -- Software Catalog Setup

"quay.io/kenosborn/inference-train-demo:v1" is my inference app prior to stephen dashboard

"quay.io/kenosborn/inference-train-demo:v2" is stephen dashboard

The RHEM catalog item that gets created "Inference (Edge AI Train Control)" has options to deploy v1 or v2.  

It calls the scratch containers that are published at quay.io/kenosborn/ai-inference-app:v#" (replacing v# with whatever the user selects

during catalog deployment).  The scratch container, in turn, pulls the inference-train-demo app that is wired to each version.

## 1. Create 'inference-{version}.container (quadlet definition) Files

### inference-v1.container

``` ini
[Unit]
Description=Inference (Edge AI train control)
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
Environment=MQTT_BROKER=192.168.100.30
Environment=MQTT_PORT=1883
Environment=MQTT_TOPIC=train/cmd
SecurityLabelDisable=true
User=root

[Install]
WantedBy=default.target
```

### inference-v1.container

``` ini
[Unit]
Description=Inference (Edge AI train control)
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
Environment=MQTT_BROKER=192.168.100.30
Environment=MQTT_PORT=1883
Environment=MQTT_TOPIC=train/cmd
SecurityLabelDisable=true
User=root

[Install]
WantedBy=default.target
```

## 2. Create and Publish Scratch Containers

### Containerfile-v1

``` dockerfile
FROM scratch
COPY inference-v1.container /inference.container
```

### Containerfile-v2

``` dockerfile
FROM scratch
COPY inference-v2.container /inference.container
```

### Build and Push Commands

``` bash
podman build --no-cache -t quay.io/kenosborn/ai-inference-app:v1 -f Containerfile-v1
podman build --no-cache -t quay.io/kenosborn/ai-inference-app:v2 -f Containerfile-v2
podman push quay.io/kenosborn/ai-inference-app:v1
podman push quay.io/kenosborn/ai-inference-app:v2
```

## 4. Create Catalog (`edge-ai-apps-catalog.yaml`)

``` yaml
apiVersion: flightctl.io/v1alpha1
kind: Catalog
metadata:
  name: edge-ai-apps
spec:
  displayName: Edge AI Apps
```

## 4. Create Catalog Item (`inference-app.yaml`)

``` yaml
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
      uri: quay.io/kenosborn/ai-inference-app
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
        MQTT_ENABLED: "true"
        MQTT_BROKER: "192.168.100.30"
        MQTT_PORT: "1883"
        MQTT_TOPIC: "train/cmd"
```

## 5. Apply Catalog and Catalog Item

``` bash
flightctl apply -f edge-ai-apps-catalog.yaml
flightctl apply -f inference-app.yaml
```

## 6. Apply the 'dummy' Catalog and Catalog Items
