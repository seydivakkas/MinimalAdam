// Embedded demos: no runtime network request required.
export const SAMPLES = {
  "01-yazilim-mimarisi": {
    "version": 1,
    "mode": "architecture",
    "concept": "Temsili bir web uygulamasında istek ve veri kalıcılığı",
    "nodes": [
      {
        "id": "ui",
        "label": "İstemci",
        "kind": "client",
        "x": 0.13,
        "y": 0.42,
        "w": 0.15,
        "h": 0.17
      },
      {
        "id": "api",
        "label": "API Katmanı",
        "kind": "service",
        "x": 0.37,
        "y": 0.42,
        "w": 0.18,
        "h": 0.17,
        "accent": "orange"
      },
      {
        "id": "logic",
        "label": "İş Mantığı",
        "kind": "process",
        "x": 0.62,
        "y": 0.42,
        "w": 0.17,
        "h": 0.17
      },
      {
        "id": "db",
        "label": "Veritabanı",
        "kind": "data",
        "x": 0.87,
        "y": 0.42,
        "w": 0.16,
        "h": 0.17,
        "accent": "blue"
      },
      {
        "id": "outside",
        "label": "Harici Servis",
        "kind": "service",
        "x": 0.62,
        "y": 0.72,
        "w": 0.19,
        "h": 0.17
      }
    ],
    "edges": [
      {
        "from": "ui",
        "to": "api",
        "kind": "data"
      },
      {
        "from": "api",
        "to": "logic",
        "kind": "data"
      },
      {
        "from": "logic",
        "to": "db",
        "kind": "data"
      },
      {
        "from": "logic",
        "to": "outside",
        "kind": "control"
      }
    ],
    "minimaladam": {
      "x": 0.239,
      "y": 0.42,
      "action": "connect",
      "edge": 0,
      "scale": 1.0
    }
  },
  "02-veri-akisi": {
    "version": 1,
    "mode": "data-flow",
    "concept": "Temsili ham veri işleme ve rapor üretme akışı",
    "nodes": [
      {
        "id": "raw",
        "label": "Ham Veri",
        "kind": "data",
        "x": 0.13,
        "y": 0.49,
        "w": 0.155,
        "h": 0.18
      },
      {
        "id": "clean",
        "label": "Temizleme",
        "kind": "process",
        "x": 0.37,
        "y": 0.49,
        "w": 0.17,
        "h": 0.18,
        "accent": "orange"
      },
      {
        "id": "validate",
        "label": "Doğrulama",
        "kind": "process",
        "x": 0.62,
        "y": 0.49,
        "w": 0.18,
        "h": 0.18
      },
      {
        "id": "report",
        "label": "Rapor",
        "kind": "result",
        "x": 0.87,
        "y": 0.49,
        "w": 0.15,
        "h": 0.18,
        "accent": "blue"
      }
    ],
    "edges": [
      {
        "from": "raw",
        "to": "clean",
        "kind": "data"
      },
      {
        "from": "clean",
        "to": "validate",
        "kind": "data"
      },
      {
        "from": "validate",
        "to": "report",
        "kind": "data"
      }
    ],
    "minimaladam": {
      "x": 0.25,
      "y": 0.49,
      "action": "carry",
      "edge": 0,
      "scale": 1.0
    }
  },
  "03-ml-pipeline": {
    "version": 1,
    "mode": "ml-pipeline",
    "concept": "Temsili model eğitimi ve tahmin hatlarının ayrımı",
    "nodes": [
      {
        "id": "train_data",
        "label": "Eğitim Verisi",
        "kind": "data",
        "x": 0.15,
        "y": 0.3,
        "w": 0.19,
        "h": 0.18
      },
      {
        "id": "train",
        "label": "Eğitim",
        "kind": "process",
        "x": 0.45,
        "y": 0.3,
        "w": 0.17,
        "h": 0.18,
        "accent": "orange"
      },
      {
        "id": "artifact",
        "label": "Model Dosyası",
        "kind": "model",
        "x": 0.74,
        "y": 0.3,
        "w": 0.21,
        "h": 0.18,
        "accent": "blue"
      },
      {
        "id": "new_data",
        "label": "Yeni Veri",
        "kind": "data",
        "x": 0.25,
        "y": 0.72,
        "w": 0.18,
        "h": 0.18
      },
      {
        "id": "prediction",
        "label": "Tahmin",
        "kind": "result",
        "x": 0.66,
        "y": 0.72,
        "w": 0.19,
        "h": 0.18,
        "accent": "orange"
      }
    ],
    "edges": [
      {
        "from": "train_data",
        "to": "train",
        "kind": "data"
      },
      {
        "from": "train",
        "to": "artifact",
        "kind": "data"
      },
      {
        "from": "new_data",
        "to": "prediction",
        "kind": "data"
      },
      {
        "from": "artifact",
        "to": "prediction",
        "kind": "control",
        "from_port": "right",
        "to_port": "right",
        "via": [
          [
            0.89,
            0.3
          ],
          [
            0.89,
            0.72
          ]
        ]
      }
    ],
    "minimaladam": {
      "x": 0.862,
      "y": 0.535,
      "action": "carry",
      "edge": 3,
      "scale": 1.17
    }
  },
  "04-muhendislik-sistemi": {
    "version": 1,
    "mode": "engineering-system",
    "concept": "Temsili sensör-denetleyici-eyleyici geri besleme sistemi",
    "nodes": [
      {
        "id": "sensor",
        "label": "Sensör",
        "kind": "sensor",
        "x": 0.17,
        "y": 0.35,
        "w": 0.16,
        "h": 0.18,
        "accent": "blue"
      },
      {
        "id": "controller",
        "label": "Denetleyici",
        "kind": "process",
        "x": 0.48,
        "y": 0.35,
        "w": 0.19,
        "h": 0.18,
        "accent": "orange"
      },
      {
        "id": "actuator",
        "label": "Eyleyici",
        "kind": "actuator",
        "x": 0.79,
        "y": 0.35,
        "w": 0.17,
        "h": 0.18
      },
      {
        "id": "plant",
        "label": "Fiziksel Sistem",
        "kind": "system",
        "x": 0.79,
        "y": 0.66,
        "w": 0.2,
        "h": 0.18
      }
    ],
    "edges": [
      {
        "from": "sensor",
        "to": "controller",
        "kind": "data"
      },
      {
        "from": "controller",
        "to": "actuator",
        "kind": "control"
      },
      {
        "from": "actuator",
        "to": "plant",
        "kind": "physical"
      },
      {
        "from": "plant",
        "to": "sensor",
        "kind": "feedback",
        "from_port": "bottom",
        "to_port": "bottom",
        "via": [
          [
            0.79,
            0.84
          ],
          [
            0.17,
            0.84
          ]
        ],
        "label": "Geri Besleme"
      }
    ],
    "minimaladam": {
      "x": 0.605,
      "y": 0.365,
      "action": "connect",
      "edge": 1,
      "scale": 1.0
    }
  }
};
