# Edge AI Inference App -- Software Catalog Setup

## 1. Create `inference-v#.container` Files

### v1

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
Environment=MQTT_BROKER=10.20.0.150
Environment=MQTT_PORT=1883
Environment=MQTT_TOPIC=train/cmd
SecurityLabelDisable=true
User=root

[Install]
WantedBy=default.target
```

### v2

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
Environment=MQTT_BROKER=10.20.0.150
Environment=MQTT_PORT=1883
Environment=MQTT_TOPIC=train/cmd
SecurityLabelDisable=true
User=root

[Install]
WantedBy=default.target
```

## 2. Create and Publish Scratch Containers

### Containerfile (v1)

``` dockerfile
FROM scratch
COPY inference-v1.container /inference.container
```

### Containerfile (v2)

``` dockerfile
FROM scratch
COPY inference-v2.container /inference.container
```

### Build Commands

``` bash
podman build --no-cache -t quay.io/kenosborn/ai-inference-app:v1 Containerfile-v1
podman build --no-cache -t quay.io/kenosborn-ai-inference-app:v2 Containerfile-v2
```

## 3. Create Catalog Item (`app-inference.yaml`)

``` yaml
# (content truncated for brevity in file generation)
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

## 5. Apply Catalog and Catalog Item

``` bash
flightctl apply -f edge-ai-apps-catalog.yaml
flightctl apply -f inference-app.yaml
```

