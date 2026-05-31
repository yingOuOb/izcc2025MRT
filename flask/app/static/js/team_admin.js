//ready
document.addEventListener("DOMContentLoaded", () => {
    mission_label();
    get_pos();
    // showDistance();
});

function get_pos() {
    const team = document.querySelector("#team").innerHTML;
    fetch(`/api/team/${team}`)
        .then(response => response.json())
        .then(data => {
           cur_location = data.location;
           target_location = data.target_location;
           document.getElementById("target_pos_label").textContent = `目標站點 : ${target_location}`;
           document.getElementById("pos_label").textContent = `目前位置 : ${cur_location}`;
        })
}

function mission_label() {
    const team = document.querySelector("#team").innerHTML;
    fetch(`/api/team/${team}`)
        .then(response => response.json())
        .then(data => {
            if (data.current_mission_finished) {
                if (data.location !== data.target_location) {
                    document.getElementById("mission_label").textContent = "目前狀態 : 移動中 請前往目標站點後按抵達站點";
                }
                else if(data.is_imprisoned){
                    document.getElementById("mission_label").textContent = "目前狀態 : 監獄 請等倒數結束後執行骰子";
                }
                else {
                    document.getElementById("mission_label").textContent = "目前狀態 : 沒有進行中的任務 請按骰子";
                }
            }
            else {
                document.getElementById("mission_label").textContent = "目前狀態 : 任務進行中 請按任務完成";
            }
        })
}

async function finish_mission() {
    const team = document.querySelector("#team").innerHTML;
    try {
        const response = await fetch(`/api/finish_mission/${team}`);
        const responseText = await response.text();

        if (responseText === "Success" || responseText === "成功") {
            await Swal.fire({
                title: "任務完成",
                icon: "success",
                confirmButtonText: "OK",
                willClose: () => {
                    mission_label();
                }
            });
        } else if (responseText.includes("card")) {
            const result = await Swal.fire({
                title: "抽卡時間",
                icon: "info",
                text: "Card time!",
                showConfirmButton: true,
                confirmButtonText: "關閉",
                showCancelButton: true,
                cancelButtonText: "前往",
                customClass: { cancelButton: 'swal-button-yellow' }
            });

            // Handle the result of the Swal.fire
            if (result.isDismissed && result.dismiss === Swal.DismissReason.cancel) {
                window.location.href = "/card";
            }
        } else {
            await Swal.fire({
                title: responseText,
                icon: "warning",
                confirmButtonText: "OK"
            });
        }
    } catch (error) {
        console.error('Error finishing mission:', error);
        await Swal.fire({
            title: "錯誤",
            text: "無法完成任務，請稍後再試。",
            icon: "error",
            confirmButtonText: "OK"
        });
    }
}


function skip_mission() {
    const team = document.querySelector("#team").innerHTML;
    fetch(`/api/skip_mission/${team}`).then(response => response.text())
        .then(response => {
            if (response === "Success" || response === "成功") {
                Swal.fire({
                    title: "成功放棄",
                    icon: "success",
                    confirmButtonText: "OK",
                    willClose: () => {
                        mission_label();
                    }
                });
            }
            else {
                Swal.fire({
                    title: response,
                    icon: "warning",
                    confirmButtonText: "OK"
                });
            }
        })
}

function missionAPI() {
    const team = document.querySelector("#team").innerHTML;
    fetch(`/api/team/${team}`)
        .then(response => response.json())
        .then(data => {
            if (data.current_mission_finished) {
                if (data.location !== data.target_location) {
                    Swal.fire({
                        icon: "warning",
                        title: "請先抵達目標站點",
                        text: "Please arrive at the target station first.",
                        confirmButtonText: "Close"
                    });
                } else {
                    window.location.href = "/dice";
                }
            }
            else {
                Swal.fire({
                    title: "請先完成任務",
                    icon: "warning",
                    text: "Please finish mission first.",
                    confirmButtonText: "Close"
                });
            }
        })
}

function arrive_target() {
    const team = document.querySelector("#team").innerHTML;
    fetch(`/api/arrive_target/${team}`).then(response => response.text())
        .then(response => {
            if (response === "Success" || response === "成功") {
                Swal.fire({
                    title: "成功抵達",
                    icon: "success",
                    confirmButtonText: "OK",
                    willClose: () => {
                        mission_label();
                        get_pos();
                    }
                });
            }
            else {
                Swal.fire({
                    title: "錯誤",
                    text: "無法完成指令，請稍後再試。",
                    icon: "warning",
                    confirmButtonText: "OK"
                });
            }
        })
}

const BEACON_SCAN_DURATION_MS = 2500;
const APPLE_COMPANY_IDENTIFIER = 0x004c;

function pickNearestBeacon(beacons) {
    if (!Array.isArray(beacons) || beacons.length === 0) {
        return null;
    }

    const scored = beacons.map(beacon => {
        const accuracy = Number(beacon.accuracy);
        const rssi = Number(beacon.rssi);
        return {
            beacon,
            accuracy: Number.isFinite(accuracy) && accuracy > 0
                ? accuracy
                : Number.POSITIVE_INFINITY,
            rssi: Number.isFinite(rssi) ? rssi : Number.NEGATIVE_INFINITY
        };
    });

    scored.sort((a, b) => {
        if (a.accuracy !== b.accuracy) {
            return a.accuracy - b.accuracy;
        }
        return b.rssi - a.rssi;
    });

    return scored[0].beacon;
}

function scanWithHtml5Plus() {
    const ibeacon = window.plus.ibeacon;

    return new Promise((resolve, reject) => {
        const stopDiscovery = () => {
            try {
                ibeacon.stopBeaconDiscovery({});
            } catch (error) {
                console.warn("Failed to stop HTML5+ beacon discovery:", error);
            }
        };

        ibeacon.startBeaconDiscovery({
            success: () => {
                setTimeout(() => {
                    ibeacon.getBeacons({
                        success: event => {
                            stopDiscovery();
                            resolve(pickNearestBeacon(event.beacons));
                        },
                        fail: error => {
                            stopDiscovery();
                            reject(error);
                        }
                    });
                }, BEACON_SCAN_DURATION_MS);
            },
            fail: reject
        });
    });
}

function formatUuid(bytes) {
    const hex = Array.from(bytes, byte => byte.toString(16).padStart(2, "0")).join("");
    return `${hex.slice(0, 8)}-${hex.slice(8, 12)}-${hex.slice(12, 16)}-${hex.slice(16, 20)}-${hex.slice(20)}`;
}

function parseIBeaconAdvertisement(event) {
    const manufacturerData = event.manufacturerData;
    const appleData = manufacturerData && manufacturerData.get(APPLE_COMPANY_IDENTIFIER);
    if (!appleData || appleData.byteLength < 23) {
        return null;
    }

    const bytes = new Uint8Array(appleData.buffer, appleData.byteOffset, appleData.byteLength);
    if (bytes[0] !== 0x02 || bytes[1] !== 0x15) {
        return null;
    }

    return {
        uuid: formatUuid(bytes.slice(2, 18)),
        major: (bytes[18] << 8) | bytes[19],
        minor: (bytes[20] << 8) | bytes[21],
        rssi: event.rssi
    };
}

function getBluetoothApi() {
    return navigator.bluetooth || window.bluetooth;
}

async function scanWithWebBluetooth() {
    const bluetooth = getBluetoothApi();
    const beacons = new Map();
    const onAdvertisement = event => {
        const beacon = parseIBeaconAdvertisement(event);
        if (!beacon) {
            return;
        }

        const key = `${beacon.uuid}/${beacon.major}/${beacon.minor}`;
        const previous = beacons.get(key);
        if (!previous || Number(beacon.rssi) > Number(previous.rssi)) {
            beacons.set(key, beacon);
        }
    };

    bluetooth.addEventListener("advertisementreceived", onAdvertisement);

    let scan;
    try {
        scan = await bluetooth.requestLEScan({
            acceptAllAdvertisements: true,
            keepRepeatedDevices: true
        });
        await new Promise(resolve => setTimeout(resolve, BEACON_SCAN_DURATION_MS));
    } finally {
        if (scan) {
            scan.stop();
        }
        bluetooth.removeEventListener("advertisementreceived", onAdvertisement);
    }

    return pickNearestBeacon(Array.from(beacons.values()));
}

async function scanWithBluetoothWatchAdvertisements() {
    const bluetooth = getBluetoothApi();
    const beacons = new Map();
    const abortController = new AbortController();
    const onAdvertisement = event => {
        const beacon = parseIBeaconAdvertisement(event);
        if (!beacon) {
            return;
        }

        const key = `${beacon.uuid}/${beacon.major}/${beacon.minor}`;
        const previous = beacons.get(key);
        if (!previous || Number(beacon.rssi) > Number(previous.rssi)) {
            beacons.set(key, beacon);
        }
    };

    bluetooth.addEventListener("advertisementreceived", onAdvertisement);

    let watcher;
    try {
        watcher = await bluetooth.watchAdvertisements({
            acceptAllAdvertisements: true,
            keepRepeatedDevices: true,
            signal: abortController.signal
        });
        await new Promise(resolve => setTimeout(resolve, BEACON_SCAN_DURATION_MS));
    } finally {
        abortController.abort();
        if (watcher && typeof watcher.stop === "function") {
            watcher.stop();
        }
        if (typeof bluetooth.unwatchAdvertisements === "function") {
            bluetooth.unwatchAdvertisements();
        }
        bluetooth.removeEventListener("advertisementreceived", onAdvertisement);
    }

    return pickNearestBeacon(Array.from(beacons.values()));
}

async function showDetectedBeacon(beacon) {
    await Swal.fire({
        title: "偵測到 Beacon",
        text: [
            `UUID: ${beacon.uuid}`,
            `Major: ${beacon.major}`,
            `Minor: ${beacon.minor}`,
            `RSSI: ${beacon.rssi ?? "未知"}`
        ].join("\n"),
        icon: "success",
        confirmButtonText: "OK"
    });
}

async function sendBeaconPos() {
    const team = document.querySelector("#team").innerHTML;
    const bluetooth = getBluetoothApi();
    const hasHtml5Plus = window.plus && window.plus.ibeacon;
    const hasBluetoothWatchAdvertisements = bluetooth
        && typeof bluetooth.watchAdvertisements === "function"
        && typeof bluetooth.addEventListener === "function";
    const hasWebBluetoothScan = bluetooth
        && typeof bluetooth.requestLEScan === "function"
        && typeof bluetooth.addEventListener === "function";
    const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent)
        || (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1);

    if (!hasHtml5Plus && !hasBluetoothWatchAdvertisements && isIOS) {
        await Swal.fire({
            title: "iPhone 瀏覽器無法掃描 Beacon",
            text: "Safari 和 Chrome 無法讓一般網頁掃描 iBeacon。請改用 Bluefy，並在 Bluefy 設定中允許 Watch Advertisements。",
            icon: "warning",
            confirmButtonText: "OK"
        });
        return;
    }

    if (!hasHtml5Plus && !window.isSecureContext) {
        await Swal.fire({
            title: "需要 HTTPS",
            text: "瀏覽器僅允許 HTTPS 網頁使用 Web Bluetooth。",
            icon: "warning",
            confirmButtonText: "OK"
        });
        return;
    }

    if (!hasHtml5Plus && !hasBluetoothWatchAdvertisements && !hasWebBluetoothScan) {
        await Swal.fire({
            title: "此瀏覽器沒有 Beacon 掃描 API",
            text: "請在 iPhone 使用 Bluefy，或在支援 requestLEScan() 的 Chrome 測試。一般瀏覽器無法掃描 iBeacon 廣播。",
            icon: "warning",
            confirmButtonText: "OK"
        });
        return;
    }

    try {
        const beacon = hasHtml5Plus
            ? await scanWithHtml5Plus()
            : hasBluetoothWatchAdvertisements
                ? await scanWithBluetoothWatchAdvertisements()
                : await scanWithWebBluetooth();

        if (!beacon) {
            await Swal.fire({
                title: "找不到 Beacon",
                text: "附近未偵測到可用的 iBeacon 裝置。",
                icon: "warning",
                confirmButtonText: "OK"
            });
            return;
        }

        await showDetectedBeacon(beacon);
        fetch(`/api/beacon/${team}/${beacon.uuid}/${beacon.major}/${beacon.minor}`)
            .then(response => response.text())
            .then(response => {
                if (response === "Success" || response === "成功") {
                    Swal.fire({
                        title: "位置更新成功",
                        icon: "success",
                        confirmButtonText: "OK",
                        willClose: () => {
                            get_pos();
                            mission_label();
                        }
                    });
                }
                else {
                    Swal.fire({
                        title: "位置更新失敗",
                        text: response,
                        icon: "warning",
                        confirmButtonText: "OK"
                    });
                }
            });
    } catch (error) {
        console.error("Error scanning beacons:", error);
        const permissionDenied = error && error.name === "NotAllowedError";
        const scanUnsupported = error && error.name === "NotSupportedError";
        await Swal.fire({
            title: "無法掃描 Beacon",
            text: permissionDenied
                ? "請允許藍牙權限後再試一次。"
                : scanUnsupported
                    ? "目前瀏覽器不支援廣播掃描。若使用 Bluefy，請在設定中允許 Watch Advertisements。"
                    : "請確認藍牙已開啟，並允許 App 使用藍牙與定位權限。若使用 Bluefy，也請開啟 Watch Advertisements。",
            icon: "error",
            confirmButtonText: "OK"
        });
    }
}
