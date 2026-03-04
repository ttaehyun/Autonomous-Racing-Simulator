# 🏎️ Clothoid-R Autonomous Driving Simulator
![Autonomous Racing Simulator](https://github.com/ttaehyun/Autonomous-Racing-Simulator/tree/main/image/background.png](https://github.com/ttaehyun/Autonomous-Racing-Simulator/blob/main/image/background.png)

본 프로젝트는 자율주행 알고리즘(Pure Pursuit, MPC, Stanley 등) 및 센서 퓨전 테스트를 위한 ROS 2 - Gazebo 기반의 차량 시뮬레이션 환경입니다.

## 🖥️ 운영 환경 (Operating Environment)
* **OS:** Ubuntu 24.04 LTS (또는 22.04 LTS)
* **ROS 2:** [Kilted]
* **Simulator:** Gazebo Sim (Ionic)
* **Dependencies:** `ros_gz_bridge`, `xacro`
---
## ⚙️ 사전 준비 및 빌드 (Installation & Build)
- **ubuntu 24.04 사용자 환경 구성 먼저 빌드 후 진행**
- **docker사용자는 환경 구성 건너뛰어도 됨**
#### 0. 환경 구성(필수 진행)
- **ROS2 kilted 설치**
Click [ROS2 kilted](https://docs.ros.org/en/kilted/Installation/Ubuntu-Install-Debs.html)
- **Gazebo Sim Ionic 설치**
Click [Gazebo Sim Ionic](https://gazebosim.org/docs/ionic/install_ubuntu/)
- **ros xacro 설치**
```bash
sudo apt install ros-kilted-xacro
```
- **ros_gz_bridge 설치**
1. Add https://packages.ros.org
```bash
 sudo sh -c 'echo "deb [arch=$(dpkg --print-architecture)] http://packages.ros.org/ros2/ubuntu $(lsb_release -cs) main" > /etc/apt/sources.list.d/ros2-latest.list'
 curl -s https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc | sudo apt-key add -
 sudo apt-get update
```
2. Install ros_gz
```bash
sudo apt install ros-kilted-ros-gz
```

----
#### 1. Git clone
```bash
git clone https://github.com/ttaehyun/Autonomous-Racing-Simulator.git
```
#### 2. Colcon build
```bash
cd ~/Autonomous-Racing-Simulator/simulate_ws 
```
```bash
colcon build --symlink-install
```

#### 3. Gazebo Sim Map 열기
```bash
gz sim -r ~/Autonomous-Racing-Simulator/simulate_ws/src/server/map/racemap.sdf 
```

#### 4. Spawn ERP42
```bash
cd ~/Autonomous-Racing-Simulator/simulate_ws
source install/setup.bash
```
**Default : car_name:=car1 x_pos:=0.8 y_pos:=1.25 z_pos:=0.3**
```bash
ros2 launch server spawn_car.launch.py
```
**차량 이름 및 위치 지정하고 싶다면 아래 명령어 실행**
```bash
ros2 launch server spawn_car.launch.py car_name:={원하는 이름} x_pos:={원하는 x좌표} y_pos:={원하는 y좌표} z_pos:={원하는 z좌표}
```
- z_pos는 되도록 0.3이상으로 할 것

#### 5. 키보드 제어 (Teleop) 노드 실행
- **현재 꾹 눌러도 입력이 되지 않음 / 한번만 눌러서 속도 방향 바꿀 수 있음**
```bash
python3 src/server/scripts/key_teleop.py
```
----

## Docker 이용
### nvidia-container-toolkit install 필수 진행
Click [here](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)
### docker pull image
```bash
docker pull rth0824/autonomous-racing-simulator:ver1.0
```
#### .sh파일 만들기
도커 파일 저장할 폴더 아무대나 .sh파일 만들기
본인은 run_docker.sh로 만듬
이후 밑 명령어 sh파일에 붙여넣기 후 저장
- **-v /home/th/~ 부분은 자기가 원하는 폴더 경로 넣어주기**
- **--name {container name} {저장한 이미지이름} 로 수정**
```bash
docker run -it --privileged \
    --gpus all \
    -e DISPLAY=$DISPLAY \
    -e __EGL_VENDOR_LIBRARY_FILENAMES=/usr/share/glvnd/egl_vendor.d/10_nvidia.json \
    --env="QT_X11_NO_MITSHM=1" \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v /dev:/dev:rw \
    -v /home/th/docker/share_24_04:/home/user/share \
    --env=LOCAL_USER_ID="$(id -u)" \
    --hostname $(hostname) \
    --network host \
    --name ubuntu_24_04 th:24.04 bash
```

- **docker 실행 후 위 1번 부터 진행**
## 🛠️ Troubleshooting (자주 묻는 질문/오류 해결)
🚨 libEGL warning 또는 센서 토픽이 출력되지 않을 때

```bash
export __EGL_VENDOR_LIBRARY_FILENAMES=/usr/share/glvnd/egl_vendor.d/10_nvidia.json
```
