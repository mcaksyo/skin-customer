// Telegram Mini App для редактора скинов Minecraft - ИСПРАВЛЕННАЯ ВЕРСИЯ
class TelegramSkinEditor {
    constructor() {
        this.canvas = document.getElementById('skinCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.previewCanvas = document.getElementById('previewCanvas');
        this.previewCtx = this.previewCanvas.getContext('2d');
        this.skinModelCanvas = document.getElementById('skinModelCanvas');
        this.skinViewer = null;
        this.skinViewerUnavailable = false;
        this.previewTexture = null;
        this.previewOverlay = document.querySelector('#previewOverlay');
        this.previewOverlay.addEventListener('change', () => this.generate3DPreview());
        
        this.skinSize = 64;
        this.currentSkin = null;
        this.textures = {};
        this.imagePool = [];
        this.textureRevision = 0;
        this.selectedParts = new Set();
        this.applyMode = 'individual';
        this.workMode = 'skin'; // 'skin' или 'cape'
        
        // Параметры 3D превью
        this.previewRotation = 0;
        this.previewScale = 7;
        
        // Регионы плащей (64x32 для стандартного, 1024x512 для HD)
        this.capeRegions = {
            'cape_back': [1, 1, 11, 17],      // Задняя часть плаща
            'cape_front': [12, 1, 22, 17],    // Передняя часть плаща
            'cape_right': [0, 1, 1, 17],      // Правая сторона
            'cape_left': [11, 1, 12, 17],     // Левая сторона
            'cape_top': [1, 0, 11, 1],        // Верх плаща
            'cape_bottom': [11, 0, 21, 1]     // Низ плаща
        };
        
        // Полные регионы скина с поддержкой второго слоя
        this.skinRegions = {
            // Голова (основной слой)
            'head_front': [8, 8, 16, 16],
            'head_back': [24, 8, 32, 16],
            'head_right': [0, 8, 8, 16],
            'head_left': [16, 8, 24, 16],
            'head_top': [8, 0, 16, 8],
            'head_bottom': [16, 0, 24, 8],
            
            // Голова (второй слой - шляпа)
            'head_overlay_front': [40, 8, 48, 16],
            'head_overlay_back': [56, 8, 64, 16],
            'head_overlay_right': [32, 8, 40, 16],
            'head_overlay_left': [48, 8, 56, 16],
            'head_overlay_top': [40, 0, 48, 8],
            'head_overlay_bottom': [48, 0, 56, 8],
            
            // Тело (основной слой)
            'body_front': [20, 20, 28, 32],
            'body_back': [32, 20, 40, 32],
            'body_right': [16, 20, 20, 32],
            'body_left': [28, 20, 32, 32],
            'body_top': [20, 16, 28, 20],
            'body_bottom': [28, 16, 36, 20],
            
            // Тело (второй слой - куртка)
            'body_overlay_front': [20, 36, 28, 48],
            'body_overlay_back': [32, 36, 40, 48],
            'body_overlay_right': [16, 36, 20, 48],
            'body_overlay_left': [28, 36, 32, 48],
            'body_overlay_top': [20, 32, 28, 36],
            'body_overlay_bottom': [28, 32, 36, 36],
            
            // Правая рука (основной слой)
            'arm_right_front': [44, 20, 48, 32],
            'arm_right_back': [52, 20, 56, 32],
            'arm_right_right': [40, 20, 44, 32],
            'arm_right_left': [48, 20, 52, 32],
            'arm_right_top': [44, 16, 48, 20],
            'arm_right_bottom': [48, 16, 52, 20],
            
            // Правая рука (второй слой - рукав)
            'arm_right_overlay_front': [44, 36, 48, 48],
            'arm_right_overlay_back': [52, 36, 56, 48],
            'arm_right_overlay_right': [40, 36, 44, 48],
            'arm_right_overlay_left': [48, 36, 52, 48],
            'arm_right_overlay_top': [44, 32, 48, 36],
            'arm_right_overlay_bottom': [48, 32, 52, 36],
            
            // Левая рука (основной слой)
            'arm_left_front': [36, 52, 40, 64],
            'arm_left_back': [44, 52, 48, 64],
            'arm_left_right': [32, 52, 36, 64],
            'arm_left_left': [40, 52, 44, 64],
            'arm_left_top': [36, 48, 40, 52],
            'arm_left_bottom': [40, 48, 44, 52],
            
            // Левая рука (второй слой - рукав)
            'arm_left_overlay_front': [52, 52, 56, 64],
            'arm_left_overlay_back': [60, 52, 64, 64],
            'arm_left_overlay_right': [48, 52, 52, 64],
            'arm_left_overlay_left': [56, 52, 60, 64],
            'arm_left_overlay_top': [52, 48, 56, 52],
            'arm_left_overlay_bottom': [56, 48, 60, 52],
            
            // Правая нога (основной слой)
            'leg_right_front': [4, 20, 8, 32],
            'leg_right_back': [12, 20, 16, 32],
            'leg_right_right': [0, 20, 4, 32],
            'leg_right_left': [8, 20, 12, 32],
            'leg_right_top': [4, 16, 8, 20],
            'leg_right_bottom': [8, 16, 12, 20],
            
            // Правая нога (второй слой - штанина)
            'leg_right_overlay_front': [4, 36, 8, 48],
            'leg_right_overlay_back': [12, 36, 16, 48],
            'leg_right_overlay_right': [0, 36, 4, 48],
            'leg_right_overlay_left': [8, 36, 12, 48],
            'leg_right_overlay_top': [4, 32, 8, 36],
            'leg_right_overlay_bottom': [8, 32, 12, 36],
            
            // Левая нога (основной слой)
            'leg_left_front': [20, 52, 24, 64],
            'leg_left_back': [28, 52, 32, 64],
            'leg_left_right': [16, 52, 20, 64],
            'leg_left_left': [24, 52, 28, 64],
            'leg_left_top': [20, 48, 24, 52],
            'leg_left_bottom': [24, 48, 28, 52],
            
            // Левая нога (второй слой - штанина)
            'leg_left_overlay_front': [4, 52, 8, 64],
            'leg_left_overlay_back': [12, 52, 16, 64],
            'leg_left_overlay_right': [0, 52, 4, 64],
            'leg_left_overlay_left': [8, 52, 12, 64],
            'leg_left_overlay_top': [4, 48, 8, 52],
            'leg_left_overlay_bottom': [8, 48, 12, 52]
        };
        
        this.partNames = {
            // Основной слой
            'head_front': 'Лицо',
            'head_back': 'Затылок',
            'head_right': 'Голова справа',
            'head_left': 'Голова слева',
            'head_top': 'Голова сверху',
            'head_bottom': 'Голова снизу',
            'body_front': 'Тело спереди',
            'body_back': 'Тело сзади',
            'body_right': 'Тело справа',
            'body_left': 'Тело слева',
            'body_top': 'Тело сверху',
            'body_bottom': 'Тело снизу',
            'arm_right_front': 'Правая рука спереди',
            'arm_right_back': 'Правая рука сзади',
            'arm_right_right': 'Правая рука справа',
            'arm_right_left': 'Правая рука слева',
            'arm_right_top': 'Правая рука сверху',
            'arm_right_bottom': 'Правая рука снизу',
            'arm_left_front': 'Левая рука спереди',
            'arm_left_back': 'Левая рука сзади',
            'arm_left_right': 'Левая рука справа',
            'arm_left_left': 'Левая рука слева',
            'arm_left_top': 'Левая рука сверху',
            'arm_left_bottom': 'Левая рука снизу',
            'leg_right_front': 'Правая нога спереди',
            'leg_right_back': 'Правая нога сзади',
            'leg_right_right': 'Правая нога справа',
            'leg_right_left': 'Правая нога слева',
            'leg_right_top': 'Правая нога сверху',
            'leg_right_bottom': 'Правая нога снизу',
            'leg_left_front': 'Левая нога спереди',
            'leg_left_back': 'Левая нога сзади',
            'leg_left_right': 'Левая нога справа',
            'leg_left_left': 'Левая нога слева',
            'leg_left_top': 'Левая нога сверху',
            'leg_left_bottom': 'Левая нога снизу',
            
            // Второй слой
            'head_overlay_front': 'Шляпа - Лицо',
            'head_overlay_back': 'Шляпа - Затылок',
            'head_overlay_right': 'Шляпа - Справа',
            'head_overlay_left': 'Шляпа - Слева',
            'head_overlay_top': 'Шляпа - Сверху',
            'head_overlay_bottom': 'Шляпа - Снизу',
            'body_overlay_front': 'Куртка - Спереди',
            'body_overlay_back': 'Куртка - Сзади',
            'body_overlay_right': 'Куртка - Справа',
            'body_overlay_left': 'Куртка - Слева',
            'body_overlay_top': 'Куртка - Сверху',
            'body_overlay_bottom': 'Куртка - Снизу',
            'arm_right_overlay_front': 'Рукав правый - Спереди',
            'arm_right_overlay_back': 'Рукав правый - Сзади',
            'arm_right_overlay_right': 'Рукав правый - Справа',
            'arm_right_overlay_left': 'Рукав правый - Слева',
            'arm_right_overlay_top': 'Рукав правый - Сверху',
            'arm_right_overlay_bottom': 'Рукав правый - Снизу',
            'arm_left_overlay_front': 'Рукав левый - Спереди',
            'arm_left_overlay_back': 'Рукав левый - Сзади',
            'arm_left_overlay_right': 'Рукав левый - Справа',
            'arm_left_overlay_left': 'Рукав левый - Слева',
            'arm_left_overlay_top': 'Рукав левый - Сверху',
            'arm_left_overlay_bottom': 'Рукав левый - Снизу',
            'leg_right_overlay_front': 'Штанина правая - Спереди',
            'leg_right_overlay_back': 'Штанина правая - Сзади',
            'leg_right_overlay_right': 'Штанина правая - Справа',
            'leg_right_overlay_left': 'Штанина правая - Слева',
            'leg_right_overlay_top': 'Штанина правая - Сверху',
            'leg_right_overlay_bottom': 'Штанина правая - Снизу',
            'leg_left_overlay_front': 'Штанина левая - Спереди',
            'leg_left_overlay_back': 'Штанина левая - Сзади',
            'leg_left_overlay_right': 'Штанина левая - Справа',
            'leg_left_overlay_left': 'Штанина левая - Слева',
            'leg_left_overlay_top': 'Штанина левая - Сверху',
            'leg_left_overlay_bottom': 'Штанина левая - Снизу'
        };
        
        this.capeNames = {
            'cape_back': 'Плащ - Задняя часть',
            'cape_front': 'Плащ - Передняя часть',
            'cape_right': 'Плащ - Правая сторона',
            'cape_left': 'Плащ - Левая сторона',
            'cape_top': 'Плащ - Верх',
            'cape_bottom': 'Плащ - Низ'
        };
        
        this.init();
    }
    
    // Получает масштабированные координаты региона
    getScaledRegion(regionName) {
        let baseCoords;
        let scale;
        
        if (this.workMode === 'cape') {
            baseCoords = this.capeRegions[regionName];
            // Для плащей: 64x32 -> 1024x512
            scale = this.skinSize / 64;
        } else {
            baseCoords = this.skinRegions[regionName];
            scale = this.skinSize / 64;
        }
        
        if (!baseCoords) return null;
        
        return [
            Math.floor(baseCoords[0] * scale),
            Math.floor(baseCoords[1] * scale),
            Math.floor(baseCoords[2] * scale),
            Math.floor(baseCoords[3] * scale)
        ];
    }
    
    getCurrentRegions() {
        return this.workMode === 'cape' ? this.capeRegions : this.skinRegions;
    }
    
    getCurrentNames() {
        return this.workMode === 'cape' ? this.capeNames : this.partNames;
    }
    
    init() {
        console.log('Initializing Telegram Skin Editor...');
        
        // Инициализация Telegram Web App
        if (window.Telegram && window.Telegram.WebApp) {
            console.log('Telegram WebApp detected');
            window.Telegram.WebApp.ready();
            window.Telegram.WebApp.expand();
        } else {
            console.log('Running in browser mode (no Telegram WebApp)');
        }
        
        this.createNewSkin();
        this.canvas.addEventListener('click', event => {
            const bounds = this.canvas.getBoundingClientRect();
            const x = (event.clientX - bounds.left) * this.currentSkin.width / bounds.width;
            const y = (event.clientY - bounds.top) * this.currentSkin.height / bounds.height;
            const part = Object.keys(this.getCurrentRegions()).find(id => {
                const [x1, y1, x2, y2] = this.getScaledRegion(id);
                return x >= x1 && x < x2 && y >= y1 && y < y2;
            });
            if (part) this.togglePart(part);
        });
    }

    textureCanvas() {
        const canvas = document.createElement('canvas');
        canvas.width = this.currentSkin.width;
        canvas.height = this.currentSkin.height;
        canvas.getContext('2d').putImageData(this.currentSkin, 0, 0);
        return canvas;
    }

    generate3DPreview() {
        const skinMode = this.workMode === 'skin';
        document.querySelector('#previewOverlayOption').hidden = !skinMode;
        const useSkinModel = skinMode && this.renderSkinModel();
        this.skinModelCanvas.hidden = !useSkinModel;
        this.previewCanvas.hidden = useSkinModel;
        if (!useSkinModel) this.renderCanvasPreview();
    }

    renderSkinModel() {
        if (this.skinViewerUnavailable || !window.skinview3d) return false;

        try {
            if (!this.skinViewer) {
                this.skinViewer = new window.skinview3d.SkinViewer({
                    canvas: this.skinModelCanvas,
                    width: 280,
                    height: 320,
                    enableControls: false,
                    renderPaused: true,
                    preserveDrawingBuffer: true,
                    zoom: 0.85
                });
            }

            if (this.previewTexture !== this.currentSkin) {
                // The editor uses the classic four-pixel arm layout at both resolutions.
                this.skinViewer.loadSkin(this.textureCanvas(), {model: 'default'});
                // Keep the editor's alpha and colors after the library's legacy-skin cleanup.
                this.skinViewer.skinCanvas.getContext('2d').putImageData(this.currentSkin, 0, 0);
                this.previewTexture = this.currentSkin;
            }

            this.skinViewer.playerObject.skin.setOuterLayerVisible(this.previewOverlay.checked);
            this.skinViewer.playerObject.rotation.y = this.previewRotation;
            this.skinViewer.render();
            return true;
        } catch (error) {
            this.skinViewer?.dispose();
            this.skinViewerUnavailable = true;
            console.warn('WebGL skin preview unavailable', error);
            return false;
        }
    }

    renderCanvasPreview() {
        const ctx = this.previewCtx;
        const {width, height} = this.previewCanvas;
        const texture = this.textureCanvas();
        const angle = this.previewRotation;
        const sin = Math.sin(angle);
        const cos = Math.cos(angle);
        const tilt = 0;
        const scale = this.previewScale;
        const cape = this.workMode === 'cape';
        const project = ([x, y, z]) => {
            const depth = x * sin + z * cos;
            return [
                width / 2 + (x * cos - z * sin) * scale,
                height / 2 + (y - (cape ? 8 : 16) + depth * tilt) * scale,
                depth - y * tilt
            ];
        };
        const boxes = cape ? [['cape', -5, 0, -0.5, 10, 16, 1]] : [
            ['head', -4, 0, -4, 8, 8, 8],
            ['body', -4, 8, -2, 8, 12, 4],
            ['arm_right', -8, 8, -2, 4, 12, 4],
            ['arm_left', 4, 8, -2, 4, 12, 4],
            ['leg_right', -4, 20, -2, 4, 12, 4],
            ['leg_left', 0, 20, -2, 4, 12, 4]
        ];
        const faces = [];
        for (const [part, x, y, z, w, h, d] of boxes) {
            const x2 = x + w, y2 = y + h, z2 = z + d;
            const sides = [
                ['front', [x, y, z2], [x2, y, z2], [x, y2, z2], cos],
                ['back', [x2, y, z], [x, y, z], [x2, y2, z], -cos],
                ['right', [x, y, z], [x, y, z2], [x, y2, z], -sin],
                ['left', [x2, y, z2], [x2, y, z], [x2, y2, z2], sin],
                ['top', [x, y, z], [x2, y, z], [x, y, z2], tilt]
            ];
            for (const [side, origin, horizontal, vertical, visibility] of sides) {
                if (visibility <= 0.0001) continue;
                const [a, b, c] = [origin, horizontal, vertical].map(project);
                faces.push({part, side, a, b, c, depth: (b[2] + c[2]) / 2});
            }
        }
        ctx.clearRect(0, 0, width, height);
        ctx.imageSmoothingEnabled = false;
        for (const {part, side, a, b, c} of faces.sort((first, second) => first.depth - second.depth)) {
            ctx.save();
            ctx.setTransform(b[0] - a[0], b[1] - a[1], c[0] - a[0], c[1] - a[1], a[0], a[1]);
            const layers = cape || !this.previewOverlay.checked ? [part] : [part, part + '_overlay'];
            for (const layer of layers) {
                const [x1, y1, x2, y2] = this.getScaledRegion(layer + '_' + side);
                ctx.drawImage(texture, x1, y1, x2 - x1, y2 - y1, 0, 0, 1, 1);
            }
            ctx.restore();
        }
    }

    rotatePreview() {
        this.previewRotation = (this.previewRotation + Math.PI / 6) % (Math.PI * 2);
        this.generate3DPreview();
    }

    resetPreview() {
        this.previewRotation = 0;
        this.generate3DPreview();
    }

    setTexture(image) {
        this.textureRevision++;
        this.currentSkin = image;
        this.skinSize = image.width;
        this.textures[this.workMode] = image;
        this.canvas.width = 320;
        this.canvas.height = 320 * image.height / image.width;
        this.updateControls();
        this.updateDisplay();
    }

    createNewSkin() {
        const height = this.workMode === 'cape' ? this.skinSize / 2 : this.skinSize;
        this.setTexture(new ImageData(this.skinSize, height));
        this.setupPartsInterface();
    }

    updateControls() {
        const cape = this.workMode === 'cape';
        for (const button of document.querySelectorAll('[data-size]')) {
            const size = Number(button.dataset.size);
            button.textContent = `${size}×${cape ? size / 2 : size}`;
            button.classList.toggle('selected', size === this.skinSize);
        }
        for (const button of document.querySelectorAll('[data-work-mode]')) {
            button.classList.toggle('selected', button.dataset.workMode === this.workMode);
        }
        document.querySelector('#wrapButton').disabled = cape;
        document.querySelector('#overlayButton').disabled = cape;
        document.querySelector('#loadButton').textContent = cape ? 'Открыть плащ' : 'Открыть скин';
        document.querySelector('#newButton').textContent = cape ? 'Новый плащ' : 'Новый скин';
    }

    updateDisplay() {
        if (!this.currentSkin) return;
        
        // Очищаем canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        this.ctx.imageSmoothingEnabled = false;
        this.ctx.drawImage(this.textureCanvas(), 0, 0, this.canvas.width, this.canvas.height);
        if (document.querySelector('#showGrid').checked) this.drawGrid();

        // Подсвечиваем выбранные части
        this.highlightSelectedParts();
    }
    
    drawGrid() {
        this.ctx.strokeStyle = 'rgba(128, 128, 128, 0.3)';
        this.ctx.lineWidth = 1;
        
        const scaleX = this.canvas.width / this.currentSkin.width;
        const scaleY = this.canvas.height / this.currentSkin.height;
        
        // Вертикальные линии
        for (let x = 0; x <= this.currentSkin.width; x += this.skinSize / 8) {
            this.ctx.beginPath();
            this.ctx.moveTo(x * scaleX, 0);
            this.ctx.lineTo(x * scaleX, this.canvas.height);
            this.ctx.stroke();
        }
        
        // Горизонтальные линии
        for (let y = 0; y <= this.currentSkin.height; y += this.skinSize / 8) {
            this.ctx.beginPath();
            this.ctx.moveTo(0, y * scaleY);
            this.ctx.lineTo(this.canvas.width, y * scaleY);
            this.ctx.stroke();
        }
    }
    
    highlightSelectedParts() {
        const scaleX = this.canvas.width / this.currentSkin.width;
        const scaleY = this.canvas.height / this.currentSkin.height;
        
        this.ctx.fillStyle = 'rgba(168, 236, 136, 0.28)';
        this.ctx.strokeStyle = 'rgba(168, 236, 136, 0.95)';
        this.ctx.lineWidth = 2;
        
        for (const partId of this.selectedParts) {
            const scaledRegion = this.getScaledRegion(partId);
            if (scaledRegion) {
                const [x1, y1, x2, y2] = scaledRegion;
                const scaledX = x1 * scaleX;
                const scaledY = y1 * scaleY;
                const scaledW = (x2 - x1) * scaleX;
                const scaledH = (y2 - y1) * scaleY;
                
                this.ctx.fillRect(scaledX, scaledY, scaledW, scaledH);
                this.ctx.strokeRect(scaledX, scaledY, scaledW, scaledH);
            }
        }
    }
    
    setupPartsInterface() {
        const container = document.getElementById('partsCategories');
        container.innerHTML = '';
        
        if (this.workMode === 'cape') {
            this.setupCapeInterface(container);
        } else {
            this.setupSkinInterface(container);
        }
    }
    
    setupCapeInterface(container) {
        const category = this.createCategory('Части плаща', true);
        
        const parts = Object.entries(this.capeNames);
        const partsContainer = category.querySelector('.category-parts');
        
        parts.forEach(([partId, partName]) => {
            const button = this.createPartButton(partId, partName);
            partsContainer.appendChild(button);
        });
        
        container.appendChild(category);
    }
    
    setupSkinInterface(container) {
        const categories = [
            {
                title: 'Голова (основной)',
                parts: Object.entries(this.partNames).filter(([id]) => 
                    id.startsWith('head_') && !id.includes('overlay'))
            },
            {
                title: 'Голова (аксессуары)',
                parts: Object.entries(this.partNames).filter(([id]) => 
                    id.startsWith('head_') && id.includes('overlay'))
            },
            {
                title: 'Тело (основной)',
                parts: Object.entries(this.partNames).filter(([id]) => 
                    id.startsWith('body_') && !id.includes('overlay'))
            },
            {
                title: 'Тело (куртка)',
                parts: Object.entries(this.partNames).filter(([id]) => 
                    id.startsWith('body_') && id.includes('overlay'))
            },
            {
                title: 'Руки (основные)',
                parts: Object.entries(this.partNames).filter(([id]) => 
                    id.startsWith('arm_') && !id.includes('overlay'))
            },
            {
                title: 'Руки (рукава)',
                parts: Object.entries(this.partNames).filter(([id]) => 
                    id.startsWith('arm_') && id.includes('overlay'))
            },
            {
                title: 'Ноги (основные)',
                parts: Object.entries(this.partNames).filter(([id]) => 
                    id.startsWith('leg_') && !id.includes('overlay'))
            },
            {
                title: 'Ноги (штанины)',
                parts: Object.entries(this.partNames).filter(([id]) => 
                    id.startsWith('leg_') && id.includes('overlay'))
            }
        ];
        
        categories.forEach((cat, index) => {
            if (cat.parts.length > 0) {
                const category = this.createCategory(cat.title, index < 2);
                const partsContainer = category.querySelector('.category-parts');
                
                cat.parts.forEach(([partId, partName]) => {
                    const button = this.createPartButton(partId, partName);
                    partsContainer.appendChild(button);
                });
                
                container.appendChild(category);
            }
        });
    }
    
    createCategory(title, expanded = false) {
        const category = document.createElement('details');
        category.className = 'category';
        category.open = expanded;

        const header = document.createElement('summary');
        header.className = 'category-header';
        header.textContent = title;

        const content = document.createElement('div');
        content.className = 'category-content';

        const partsContainer = document.createElement('div');
        partsContainer.className = 'category-parts';
        content.appendChild(partsContainer);
        category.append(header, content);

        return category;
    }
    
    createPartButton(partId, partName) {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'part-button';
        button.textContent = partName.replace(/^[^-]+ - /, ''); // Убираем префикс для краткости
        button.onclick = () => this.togglePart(partId);
        button.dataset.partId = partId;
        return button;
    }
    
    togglePart(partId) {
        if (this.selectedParts.has(partId)) {
            this.selectedParts.delete(partId);
        } else {
            this.selectedParts.add(partId);
        }
        
        this.updatePartsDisplay();
        this.updateDisplay();
    }
    
    updatePartsDisplay() {
        const buttons = document.querySelectorAll('.part-button');
        for (const button of buttons) {
            const selected = this.selectedParts.has(button.dataset.partId);
            button.classList.toggle('selected', selected);
            button.setAttribute('aria-pressed', String(selected));
        }

        const count = `Выбрано: ${this.selectedParts.size}`;
        document.querySelector('#selectionInfo').textContent = count;
        document.querySelector('#editorSelection').textContent = count;
    }
    
    selectAllParts() {
        this.selectedParts.clear();
        const allParts = Object.keys(this.getCurrentRegions());
        allParts.forEach(part => this.selectedParts.add(part));
        this.updatePartsDisplay();
        this.updateDisplay();
        this.showMessage(`Выбраны все части: ${allParts.length}`);
    }
    
    selectMainLayer() {
        this.selectedParts.clear();
        
        if (this.workMode === 'cape') {
            // Для плащей выбираем все части
            this.selectAllParts();
            return;
        }
        
        // Выбираем только основной слой (без overlay)
        const mainParts = Object.keys(this.skinRegions).filter(part => 
            !part.includes('overlay')
        );
        
        mainParts.forEach(part => this.selectedParts.add(part));
        this.updatePartsDisplay();
        this.updateDisplay();
        this.showMessage(`Выбран основной слой: ${mainParts.length} частей`);
    }
    
    selectOverlayLayer() {
        this.selectedParts.clear();
        
        if (this.workMode === 'cape') {
            this.showMessage('У плащей нет второго слоя');
            return;
        }
        
        // Выбираем только второй слой (overlay)
        const overlayParts = Object.keys(this.skinRegions).filter(part => 
            part.includes('overlay')
        );
        
        overlayParts.forEach(part => this.selectedParts.add(part));
        this.updatePartsDisplay();
        this.updateDisplay();
        this.showMessage(`Выбран второй слой: ${overlayParts.length} частей`);
    }
    
    clearSelection() {
        this.selectedParts.clear();
        this.updatePartsDisplay();
        this.updateDisplay();
    }
    
    paintRegions(paint) {
        const canvas = this.textureCanvas();
        const ctx = canvas.getContext('2d');
        ctx.imageSmoothingQuality = 'high';
        paint(ctx);
        this.setTexture(ctx.getImageData(0, 0, canvas.width, canvas.height));
    }

    selectedRegions() {
        if (!this.selectedParts.size) this.showMessage('Сначала выберите грани на развёртке или во вкладке «Части»');
        return Array.from(this.selectedParts, id => this.getScaledRegion(id));
    }

    applyImageToParts(image) {
        const regions = this.selectedRegions();
        if (!regions.length) return;
        const left = Math.min(...regions.map(region => region[0]));
        const top = Math.min(...regions.map(region => region[1]));
        const right = Math.max(...regions.map(region => region[2]));
        const bottom = Math.max(...regions.map(region => region[3]));
        this.paintRegions(ctx => {
            for (const [x1, y1, x2, y2] of regions) {
                const w = x2 - x1, h = y2 - y1;
                if (this.applyMode === 'stretch') {
                    ctx.save();
                    ctx.beginPath();
                    ctx.rect(x1, y1, w, h);
                    ctx.clip();
                    ctx.drawImage(image, left, top, right - left, bottom - top);
                    ctx.restore();
                } else {
                    ctx.drawImage(image, x1, y1, w, h);
                }
            }
        });
        this.showMessage(`Обновлено граней: ${regions.length}`);
    }

    wrapImage(image) {
        if (this.workMode !== 'skin') return;
        const layouts = [
            [['front', 'back'], [[6,0,8,9], [6,9,8,12], [2,9,4,12], [14,9,4,12], [6,21,4,15], [10,21,4,15]]],
            [['right', 'left'], [[8,0,4,9], [8,9,4,12], [4,9,4,12], [12,9,4,12], [8,21,2,15], [10,21,2,15]]],
            [['top', 'bottom'], [[6,6,8,8], [6,14,8,8], [2,14,4,4], [14,14,4,4], [6,22,4,4], [10,22,4,4]]]
        ];
        const parts = ['head', 'body', 'arm_right', 'arm_left', 'leg_right', 'leg_left'];
        this.paintRegions(ctx => {
            for (const [sides, positions] of layouts) {
                for (const side of sides) {
                    parts.forEach((part, index) => {
                        const [sx, sy, sw, sh] = positions[index];
                        const [x1, y1, x2, y2] = this.getScaledRegion(part + '_' + side);
                        const w = x2 - x1, h = y2 - y1;
                        ctx.save();
                        ctx.translate(side === 'back' ? x2 : x1, y1);
                        if (side === 'back') ctx.scale(-1, 1);
                        const sourceX = side === 'back' ? 20 - sx - sw : sx;
                        ctx.drawImage(image, sourceX * image.width / 20, sy * image.height / 36,
                            sw * image.width / 20, sh * image.height / 36, 0, 0, w, h);
                        ctx.restore();
                    });
                }
            }
        });
        this.showMessage('Изображение нанесено на шесть сторон основного слоя');
    }

    showMessage(text) {
        document.querySelector('#status').textContent = text;
    }

    downloadSkin() {
        if (!this.currentSkin) {
            this.showMessage('Нет скина для сохранения');
            return;
        }
        
        const tempCanvas = document.createElement('canvas');
        tempCanvas.width = this.currentSkin.width;
        tempCanvas.height = this.currentSkin.height;
        const tempCtx = tempCanvas.getContext('2d');
        
        tempCtx.putImageData(this.currentSkin, 0, 0);
        
        // Создаем ссылку для скачивания
        const link = document.createElement('a');
        const filename = this.workMode === 'cape' ? 'minecraft_cape.png' : 'minecraft_skin.png';
        link.download = filename;
        link.href = tempCanvas.toDataURL();
        link.click();
        
        this.showMessage(`PNG подготовлен к скачиванию: ${filename}`);
    }
}

// Глобальные переменные и функции
let skinEditor;

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    skinEditor = new TelegramSkinEditor();
});

// Функции для HTML
function switchTab(tabName) {
    if (tabName === 'preview') skinEditor.generate3DPreview();
    // Скрываем все вкладки
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Показываем выбранную вкладку
    document.getElementById(tabName).classList.add('active');
    
    // Находим и активируем соответствующую кнопку вкладки
    const tabs = document.querySelectorAll('.tab');
    const tabNames = ['editor', 'parts', 'preview'];
    const tabIndex = tabNames.indexOf(tabName);
    
    if (tabIndex !== -1 && tabs[tabIndex]) {
        tabs[tabIndex].classList.add('active');
    }
}

function loadSkin() {
    document.getElementById('skinFileInput').click();
}

async function decodeImage(file) {
    const url = URL.createObjectURL(file);
    try {
        const image = new Image();
        image.src = url;
        await image.decode();
        return image;
    } finally {
        URL.revokeObjectURL(url);
    }
}

async function withImage(event, apply) {
    const file = event.target.files[0];
    event.target.value = '';
    if (!file) return;
    const revision = skinEditor.textureRevision;
    try {
        const image = await decodeImage(file);
        if (revision === skinEditor.textureRevision) apply(image);
    } catch {
        skinEditor.showMessage('Не удалось прочитать изображение');
    }
}

function handleSkinLoad(event) {
    return withImage(event, image => {
        const {width, height} = image;
        const cape = skinEditor.workMode === 'cape';
        if (![64, 1024].includes(width) || height !== (cape ? width / 2 : width)) {
            skinEditor.showMessage(cape ? 'Размер плаща должен быть 64×32 или 1024×512' :
                'Размер скина должен быть 64×64 или 1024×1024');
            return;
        }
        const canvas = document.createElement('canvas');
        canvas.width = width;
        canvas.height = height;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(image, 0, 0);
        skinEditor.setTexture(ctx.getImageData(0, 0, width, height));
        skinEditor.showMessage(cape ? 'Плащ загружен' : 'Скин загружен');
    });
}

function saveSkin() {
    skinEditor.downloadSkin();
}

function createNewSkin() {
    if (confirm('Заменить текущую текстуру пустой?')) skinEditor.createNewSkin();
}

function selectSize(value) {
    const size = Number(value);
    if (size === skinEditor.skinSize) return;
    const texture = skinEditor.textureCanvas();
    const canvas = document.createElement('canvas');
    canvas.width = size;
    canvas.height = size * texture.height / texture.width;
    const ctx = canvas.getContext('2d');
    ctx.imageSmoothingEnabled = false;
    ctx.drawImage(texture, 0, 0, canvas.width, canvas.height);
    skinEditor.setTexture(ctx.getImageData(0, 0, canvas.width, canvas.height));
}

function loadImage() {
    if (skinEditor.selectedRegions().length) document.querySelector('#imageFileInput').click();
}

function handleImageLoad(event) {
    return withImage(event, image => skinEditor.applyImageToParts(image));
}

async function loadPool(event) {
    const files = Array.from(event.target.files);
    event.target.value = '';
    if (!files.length) return;
    const request = skinEditor.poolRequest = {};
    const results = await Promise.allSettled(files.map(decodeImage));
    if (skinEditor.poolRequest !== request) return;
    skinEditor.imagePool = results.filter(result => result.status === 'fulfilled').map(result => result.value);
    skinEditor.showMessage(`Изображений в пуле: ${skinEditor.imagePool.length} из ${files.length}`);
}

function randomizePool() {
    const pool = skinEditor.imagePool;
    if (!pool.length) {
        skinEditor.showMessage('Сначала загрузите пул изображений');
        return;
    }
    const regions = skinEditor.selectedRegions();
    if (!regions.length) return;
    skinEditor.paintRegions(ctx => {
        for (const [x1, y1, x2, y2] of regions) {
            const image = pool[Math.floor(Math.random() * pool.length)];
            ctx.drawImage(image, x1, y1, x2 - x1, y2 - y1);
        }
    });
    skinEditor.showMessage(`Обновлено граней из пула: ${regions.length}`);
}

function clearSelected() {
    const regions = skinEditor.selectedRegions();
    if (!regions.length) return;
    skinEditor.paintRegions(ctx => {
        for (const [x1, y1, x2, y2] of regions) ctx.clearRect(x1, y1, x2 - x1, y2 - y1);
    });
    skinEditor.showMessage(`Очищено граней: ${regions.length}`);
}

function selectMainLayer() { skinEditor.selectMainLayer(); }
function selectOverlayLayer() { skinEditor.selectOverlayLayer(); }
function clearSelection() { skinEditor.clearSelection(); }
function selectAllParts() { skinEditor.selectAllParts(); }

function selectWorkMode(mode) {
    if (skinEditor.workMode === mode) return;
    skinEditor.workMode = mode;
    skinEditor.selectedParts.clear();
    const texture = skinEditor.textures[mode];
    if (texture) {
        skinEditor.setTexture(texture);
        skinEditor.setupPartsInterface();
    } else {
        skinEditor.createNewSkin();
    }
}

function selectMode(mode) {
    for (const button of document.querySelectorAll('[data-apply-mode]')) {
        button.classList.toggle('selected', button.dataset.applyMode === mode);
    }
    skinEditor.applyMode = mode;
    document.querySelector('#applyHint').textContent = mode === 'stretch'
        ? 'Одно изображение распределится по общей области выбранных граней.'
        : 'Каждая выбранная грань получит полное изображение.';
}

function generate3DPreview() { skinEditor.generate3DPreview(); }
function rotatePreview() { skinEditor.rotatePreview(); }
function resetPreview() { skinEditor.resetPreview(); }
