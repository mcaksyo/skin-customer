// Telegram Mini App для редактора скинов Minecraft - ИСПРАВЛЕННАЯ ВЕРСИЯ
class TelegramSkinEditor {
    constructor() {
        this.canvas = document.getElementById('skinCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.previewCanvas = document.getElementById('previewCanvas');
        this.previewCtx = this.previewCanvas.getContext('2d');
        
        this.skinSize = 64;
        this.currentSkin = null;
        this.selectedParts = new Set();
        this.applyMode = 'individual';
        this.workMode = 'skin'; // 'skin' или 'cape'
        
        // Параметры 3D превью
        this.previewRotation = 0;
        this.previewScale = 4;
        
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
        this.setupPartsInterface();
        this.updateDisplay();
        
        console.log('Initialization complete');
    }
    
    generate3DPreview() {
        console.log('Generating 3D preview...');
        
        if (!this.currentSkin) {
            this.showMessage('Сначала создайте или загрузите скин');
            return;
        }
        
        console.log('Current skin dimensions:', this.currentSkin.width, 'x', this.currentSkin.height);
        console.log('Work mode:', this.workMode);
        
        // Очищаем превью canvas
        this.previewCtx.clearRect(0, 0, this.previewCanvas.width, this.previewCanvas.height);
        
        try {
            if (this.workMode === 'cape') {
                this.drawCapePreview();
            } else {
                this.drawSkinPreview();
            }
            
            console.log('3D preview generated successfully');
            this.showMessage('3D превью создано');
        } catch (error) {
            console.error('Error generating 3D preview:', error);
            this.showMessage('Ошибка создания превью: ' + error.message);
        }
    }
    
    drawSkinPreview() {
        const centerX = this.previewCanvas.width / 2;
        const startY = 30;
        const scale = this.previewScale;
        
        // Рисуем фон
        this.previewCtx.fillStyle = '#87CEEB';
        this.previewCtx.fillRect(0, 0, this.previewCanvas.width, this.previewCanvas.height);
        
        // Рисуем тень
        this.previewCtx.fillStyle = 'rgba(0, 0, 0, 0.2)';
        this.previewCtx.fillRect(centerX - 40, startY + 200, 80, 10);
        
        // Сохраняем контекст для поворота
        this.previewCtx.save();
        this.previewCtx.translate(centerX, startY + 100);
        this.previewCtx.rotate(this.previewRotation);
        this.previewCtx.translate(-centerX, -(startY + 100));
        
        // Рисуем голову (с тенью и объемом)
        this.drawIsometric3DPart('head_front', centerX - 16, startY, scale, false);
        this.drawIsometric3DPart('head_right', centerX + 16, startY, scale * 0.5, true);
        this.drawIsometric3DPart('head_top', centerX - 16, startY - 8, scale, false, 1.2);
        
        // Второй слой головы
        if (this.hasVisiblePart('head_overlay_front')) {
            this.drawIsometric3DPart('head_overlay_front', centerX - 16, startY, scale, false, 0.9);
            this.drawIsometric3DPart('head_overlay_right', centerX + 16, startY, scale * 0.5, true, 0.9);
            this.drawIsometric3DPart('head_overlay_top', centerX - 16, startY - 8, scale, false, 1.1);
        }
        
        // Рисуем тело
        this.drawIsometric3DPart('body_front', centerX - 16, startY + 32, scale, false);
        this.drawIsometric3DPart('body_right', centerX + 16, startY + 32, scale * 0.5, true);
        this.drawIsometric3DPart('body_top', centerX - 16, startY + 24, scale, false, 1.2);
        
        // Второй слой тела
        if (this.hasVisiblePart('body_overlay_front')) {
            this.drawIsometric3DPart('body_overlay_front', centerX - 16, startY + 32, scale, false, 0.9);
            this.drawIsometric3DPart('body_overlay_right', centerX + 16, startY + 32, scale * 0.5, true, 0.9);
        }
        
        // Рисуем руки
        this.drawIsometric3DPart('arm_right_front', centerX - 32, startY + 32, scale * 0.8, false);
        this.drawIsometric3DPart('arm_left_front', centerX + 24, startY + 32, scale * 0.8, false);
        
        // Рукава
        if (this.hasVisiblePart('arm_right_overlay_front')) {
            this.drawIsometric3DPart('arm_right_overlay_front', centerX - 32, startY + 32, scale * 0.8, false, 0.9);
        }
        if (this.hasVisiblePart('arm_left_overlay_front')) {
            this.drawIsometric3DPart('arm_left_overlay_front', centerX + 24, startY + 32, scale * 0.8, false, 0.9);
        }
        
        // Рисуем ноги
        this.drawIsometric3DPart('leg_right_front', centerX - 16, startY + 80, scale * 0.8, false);
        this.drawIsometric3DPart('leg_left_front', centerX, startY + 80, scale * 0.8, false);
        
        // Штанины
        if (this.hasVisiblePart('leg_right_overlay_front')) {
            this.drawIsometric3DPart('leg_right_overlay_front', centerX - 16, startY + 80, scale * 0.8, false, 0.9);
        }
        if (this.hasVisiblePart('leg_left_overlay_front')) {
            this.drawIsometric3DPart('leg_left_overlay_front', centerX, startY + 80, scale * 0.8, false, 0.9);
        }
        
        this.previewCtx.restore();
    }
    
    drawCapePreview() {
        const centerX = this.previewCanvas.width / 2;
        const startY = 50;
        const scale = 6;
        
        // Рисуем фон
        this.previewCtx.fillStyle = '#87CEEB';
        this.previewCtx.fillRect(0, 0, this.previewCanvas.width, this.previewCanvas.height);
        
        // Рисуем плащ
        this.drawIsometric3DPart('cape_back', centerX - 30, startY, scale, false);
        this.drawIsometric3DPart('cape_right', centerX + 30, startY, scale * 0.2, true);
        
        // Добавляем текст
        this.previewCtx.fillStyle = 'white';
        this.previewCtx.font = 'bold 16px Arial';
        this.previewCtx.textAlign = 'center';
        this.previewCtx.strokeStyle = 'black';
        this.previewCtx.lineWidth = 2;
        this.previewCtx.strokeText('Плащ', centerX, startY - 20);
        this.previewCtx.fillText('Плащ', centerX, startY - 20);
    }
    
    drawIsometric3DPart(partId, x, y, scale, darken = false, alpha = 1.0) {
        const scaledRegion = this.getScaledRegion(partId);
        if (!scaledRegion) return;
        
        const [x1, y1, x2, y2] = scaledRegion;
        const width = x2 - x1;
        const height = y2 - y1;
        
        if (width <= 0 || height <= 0) return;
        
        // Создаем временный canvas для части
        const tempCanvas = document.createElement('canvas');
        tempCanvas.width = width;
        tempCanvas.height = height;
        const tempCtx = tempCanvas.getContext('2d');
        
        // Извлекаем часть из скина
        const partImageData = new ImageData(width, height);
        
        for (let py = 0; py < height; py++) {
            for (let px = 0; px < width; px++) {
                const srcX = x1 + px;
                const srcY = y1 + py;
                
                if (srcX < this.currentSkin.width && srcY < this.currentSkin.height) {
                    const srcIndex = (srcY * this.currentSkin.width + srcX) * 4;
                    const dstIndex = (py * width + px) * 4;
                    
                    if (srcIndex < this.currentSkin.data.length) {
                        partImageData.data[dstIndex] = this.currentSkin.data[srcIndex];
                        partImageData.data[dstIndex + 1] = this.currentSkin.data[srcIndex + 1];
                        partImageData.data[dstIndex + 2] = this.currentSkin.data[srcIndex + 2];
                        partImageData.data[dstIndex + 3] = this.currentSkin.data[srcIndex + 3];
                    }
                }
            }
        }
        
        tempCtx.putImageData(partImageData, 0, 0);
        
        // Рисуем на превью canvas с эффектами
        this.previewCtx.imageSmoothingEnabled = false;
        this.previewCtx.globalAlpha = alpha;
        
        if (darken) {
            this.previewCtx.filter = 'brightness(0.6) contrast(1.2)';
        } else {
            this.previewCtx.filter = 'brightness(1.0) contrast(1.1)';
        }
        
        // Добавляем тень
        this.previewCtx.shadowColor = 'rgba(0, 0, 0, 0.3)';
        this.previewCtx.shadowBlur = 2;
        this.previewCtx.shadowOffsetX = 1;
        this.previewCtx.shadowOffsetY = 1;
        
        this.previewCtx.drawImage(tempCanvas, x, y, width * scale, height * scale);
        
        // Сбрасываем эффекты
        this.previewCtx.filter = 'none';
        this.previewCtx.globalAlpha = 1.0;
        this.previewCtx.shadowColor = 'transparent';
    }
    
    hasVisiblePart(partId) {
        const scaledRegion = this.getScaledRegion(partId);
        if (!scaledRegion) return false;
        
        const [x1, y1, x2, y2] = scaledRegion;
        
        // Проверяем несколько пикселей на прозрачность
        for (let y = y1; y < y2; y += Math.max(1, Math.floor((y2 - y1) / 4))) {
            for (let x = x1; x < x2; x += Math.max(1, Math.floor((x2 - x1) / 4))) {
                const index = (y * this.currentSkin.width + x) * 4 + 3;
                if (index < this.currentSkin.data.length && this.currentSkin.data[index] > 10) {
                    return true;
                }
            }
        }
        return false;
    }
    
    rotatePreview() {
        this.previewRotation += Math.PI / 4; // Поворот на 45 градусов
        if (this.previewRotation >= Math.PI * 2) {
            this.previewRotation = 0;
        }
        this.generate3DPreview();
    }
    
    resetPreview() {
        this.previewRotation = 0;
        this.previewScale = 4;
        this.generate3DPreview();
    }
    
    createNewSkin() {
        if (this.workMode === 'cape') {
            // Плащи: 64x32 или 1024x512
            const width = this.skinSize;
            const height = this.skinSize / 2;
            this.currentSkin = new ImageData(width, height);
            
            // Обновляем размер canvas для плащей
            this.canvas.width = 320;
            this.canvas.height = 160;
        } else {
            // Скины: 64x64 или 1024x1024
            this.currentSkin = new ImageData(this.skinSize, this.skinSize);
            
            // Обновляем размер canvas для скинов
            this.canvas.width = 320;
            this.canvas.height = 320;
        }
        
        // Заполняем прозрачным цветом
        for (let i = 0; i < this.currentSkin.data.length; i += 4) {
            this.currentSkin.data[i] = 0;     // R
            this.currentSkin.data[i + 1] = 0; // G
            this.currentSkin.data[i + 2] = 0; // B
            this.currentSkin.data[i + 3] = 0; // A
        }
        this.updateDisplay();
        this.setupPartsInterface();
    }
    
    updateDisplay() {
        if (!this.currentSkin) return;
        
        // Очищаем canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Создаем временный canvas для скина
        const tempCanvas = document.createElement('canvas');
        tempCanvas.width = this.currentSkin.width;
        tempCanvas.height = this.currentSkin.height;
        const tempCtx = tempCanvas.getContext('2d');
        
        // Рисуем скин
        tempCtx.putImageData(this.currentSkin, 0, 0);
        
        // Масштабируем и отображаем
        this.ctx.imageSmoothingEnabled = false;
        this.ctx.drawImage(tempCanvas, 0, 0, this.canvas.width, this.canvas.height);
        
        // Рисуем сетку
        this.drawGrid();
        
        // Подсвечиваем выбранные части
        this.highlightSelectedParts();
    }
    
    drawGrid() {
        this.ctx.strokeStyle = 'rgba(128, 128, 128, 0.3)';
        this.ctx.lineWidth = 1;
        
        const scaleX = this.canvas.width / this.currentSkin.width;
        const scaleY = this.canvas.height / this.currentSkin.height;
        
        // Вертикальные линии
        for (let x = 0; x <= this.currentSkin.width; x += 8) {
            this.ctx.beginPath();
            this.ctx.moveTo(x * scaleX, 0);
            this.ctx.lineTo(x * scaleX, this.canvas.height);
            this.ctx.stroke();
        }
        
        // Горизонтальные линии
        for (let y = 0; y <= this.currentSkin.height; y += 8) {
            this.ctx.beginPath();
            this.ctx.moveTo(0, y * scaleY);
            this.ctx.lineTo(this.canvas.width, y * scaleY);
            this.ctx.stroke();
        }
    }
    
    highlightSelectedParts() {
        const scaleX = this.canvas.width / this.currentSkin.width;
        const scaleY = this.canvas.height / this.currentSkin.height;
        
        this.ctx.fillStyle = 'rgba(0, 122, 255, 0.3)';
        this.ctx.strokeStyle = 'rgba(0, 122, 255, 0.8)';
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
        const category = this.createCategory('Части плаща', 'cape-parts', true);
        
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
                const category = this.createCategory(cat.title, `category-${index}`, index < 2);
                const partsContainer = category.querySelector('.category-parts');
                
                cat.parts.forEach(([partId, partName]) => {
                    const button = this.createPartButton(partId, partName);
                    partsContainer.appendChild(button);
                });
                
                container.appendChild(category);
            }
        });
    }
    
    createCategory(title, id, expanded = false) {
        const category = document.createElement('div');
        category.className = 'category';
        
        const header = document.createElement('div');
        header.className = 'category-header';
        header.innerHTML = `
            <span>${title}</span>
            <span class="expand-icon">${expanded ? '▼' : '▶'}</span>
        `;
        
        const content = document.createElement('div');
        content.className = `category-content ${expanded ? 'expanded' : ''}`;
        
        const partsContainer = document.createElement('div');
        partsContainer.className = 'category-parts';
        content.appendChild(partsContainer);
        
        header.onclick = () => {
            const isExpanded = content.classList.contains('expanded');
            content.classList.toggle('expanded');
            header.querySelector('.expand-icon').textContent = isExpanded ? '▶' : '▼';
        };
        
        category.appendChild(header);
        category.appendChild(content);
        
        return category;
    }
    
    createPartButton(partId, partName) {
        const button = document.createElement('div');
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
        buttons.forEach(button => {
            const partId = button.dataset.partId;
            if (this.selectedParts.has(partId)) {
                button.classList.add('selected');
            } else {
                button.classList.remove('selected');
            }
        });
        
        document.getElementById('selectionInfo').textContent = 
            `Выбрано: ${this.selectedParts.size} частей`;
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
    
    applyImageToParts(imageData) {
        if (this.selectedParts.size === 0) {
            this.showMessage('Выберите части для применения изображения');
            return;
        }
        
        const tempCanvas = document.createElement('canvas');
        const tempCtx = tempCanvas.getContext('2d');
        
        for (const partId of this.selectedParts) {
            const scaledRegion = this.getScaledRegion(partId);
            if (!scaledRegion) continue;
            
            const [x1, y1, x2, y2] = scaledRegion;
            const width = x2 - x1;
            const height = y2 - y1;
            
            // Масштабируем изображение под размер части
            tempCanvas.width = width;
            tempCanvas.height = height;
            tempCtx.clearRect(0, 0, width, height);
            tempCtx.drawImage(imageData, 0, 0, width, height);
            
            // Получаем данные пикселей
            const partImageData = tempCtx.getImageData(0, 0, width, height);
            
            // Применяем к скину
            this.applyImageDataToRegion(partImageData, x1, y1, width, height);
        }
        
        this.updateDisplay();
        this.showMessage(`Изображение применено к ${this.selectedParts.size} частям`);
    }
    
    applyImageDataToRegion(imageData, startX, startY, width, height) {
        for (let y = 0; y < height; y++) {
            for (let x = 0; x < width; x++) {
                const srcIndex = (y * width + x) * 4;
                const dstIndex = ((startY + y) * this.currentSkin.width + (startX + x)) * 4;
                
                if (dstIndex < this.currentSkin.data.length && srcIndex < imageData.data.length) {
                    this.currentSkin.data[dstIndex] = imageData.data[srcIndex];
                    this.currentSkin.data[dstIndex + 1] = imageData.data[srcIndex + 1];
                    this.currentSkin.data[dstIndex + 2] = imageData.data[srcIndex + 2];
                    this.currentSkin.data[dstIndex + 3] = imageData.data[srcIndex + 3];
                }
            }
        }
    }
    
    // Удаляем старые методы превью - теперь используем skinview3d
    
    getPartWidth(partType) {
        const regions = {
            'head': 8, 'body': 8, 'arm_right': 4, 'arm_left': 4, 'leg_right': 4, 'leg_left': 4
        };
        return regions[partType] || 8;
    }
    
    getPartDepth(partType) {
        const regions = {
            'head': 8, 'body': 4, 'arm_right': 4, 'arm_left': 4, 'leg_right': 4, 'leg_left': 4
        };
        return regions[partType] || 4;
    }
    
    showMessage(text) {
        if (window.Telegram && window.Telegram.WebApp) {
            window.Telegram.WebApp.showAlert(text);
        } else {
            alert(text);
        }
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
        
        this.showMessage(`${this.workMode === 'cape' ? 'Плащ' : 'Скин'} сохранен`);
    }
}

// Глобальные переменные и функции
let skinEditor;

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    skinEditor = new TelegramSkinEditor();
});

// Функции для HTML
function switchTab(tabName) {
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
    const tabTexts = ['Редактор', 'Части', 'Превью'];
    const tabNames = ['editor', 'parts', 'preview'];
    const tabIndex = tabNames.indexOf(tabName);
    
    if (tabIndex !== -1 && tabs[tabIndex]) {
        tabs[tabIndex].classList.add('active');
    }
}

function loadSkin() {
    document.getElementById('skinFileInput').click();
}

function handleSkinLoad(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    const img = new Image();
    img.onload = function() {
        let validSize = false;
        
        if (skinEditor.workMode === 'cape') {
            // Плащи должны быть 64x32 или 1024x512
            if ((img.width === 64 && img.height === 32) || 
                (img.width === 1024 && img.height === 512)) {
                validSize = true;
                skinEditor.skinSize = img.width;
            }
        } else {
            // Скины должны быть квадратными 64x64 или 1024x1024
            if (img.width === img.height && (img.width === 64 || img.width === 1024)) {
                validSize = true;
                skinEditor.skinSize = img.width;
            }
        }
        
        if (validSize) {
            // Создаем canvas для загрузки
            const tempCanvas = document.createElement('canvas');
            tempCanvas.width = img.width;
            tempCanvas.height = img.height;
            const tempCtx = tempCanvas.getContext('2d');
            
            tempCtx.drawImage(img, 0, 0);
            skinEditor.currentSkin = tempCtx.getImageData(0, 0, img.width, img.height);
            
            // Обновляем размер canvas
            if (skinEditor.workMode === 'cape') {
                skinEditor.canvas.width = 320;
                skinEditor.canvas.height = 160;
            } else {
                skinEditor.canvas.width = 320;
                skinEditor.canvas.height = 320;
            }
            
            skinEditor.updateDisplay();
            skinEditor.setupPartsInterface();
            
            const itemType = skinEditor.workMode === 'cape' ? 'Плащ' : 'Скин';
            skinEditor.showMessage(`${itemType} загружен успешно`);
        } else {
            const expectedSizes = skinEditor.workMode === 'cape' ? 
                '64x32 или 1024x512' : '64x64 или 1024x1024';
            skinEditor.showMessage(`${skinEditor.workMode === 'cape' ? 'Плащ' : 'Скин'} должен быть ${expectedSizes}`);
        }
    };
    img.src = URL.createObjectURL(file);
}

function saveSkin() {
    skinEditor.downloadSkin();
}

function createNewSkin() {
    skinEditor.createNewSkin();
    skinEditor.showMessage('Создан новый скин');
}

function selectSize(size) {
    document.querySelectorAll('.size-option').forEach(opt => opt.classList.remove('selected'));
    
    // Находим кнопку по тексту
    const buttons = document.querySelectorAll('.size-option');
    buttons.forEach(btn => {
        if ((size === '64' && btn.textContent.includes('64x64')) ||
            (size === '1024' && btn.textContent.includes('1024x1024'))) {
            btn.classList.add('selected');
        }
    });
    
    skinEditor.skinSize = parseInt(size);
    skinEditor.createNewSkin();
}

function loadImage() {
    document.getElementById('imageFileInput').click();
}

function handleImageLoad(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    const img = new Image();
    img.onload = function() {
        skinEditor.applyImageToParts(img);
    };
    img.src = URL.createObjectURL(file);
}

function clearSelected() {
    if (skinEditor.selectedParts.size === 0) {
        skinEditor.showMessage('Нет выбранных частей для очистки');
        return;
    }
    
    // Очищаем выбранные части
    for (const partId of skinEditor.selectedParts) {
        const scaledRegion = skinEditor.getScaledRegion(partId);
        if (!scaledRegion) continue;
        
        const [x1, y1, x2, y2] = scaledRegion;
        
        // Заполняем прозрачным цветом
        for (let y = y1; y < y2; y++) {
            for (let x = x1; x < x2; x++) {
                const index = (y * skinEditor.currentSkin.width + x) * 4;
                if (index < skinEditor.currentSkin.data.length) {
                    skinEditor.currentSkin.data[index] = 0;
                    skinEditor.currentSkin.data[index + 1] = 0;
                    skinEditor.currentSkin.data[index + 2] = 0;
                    skinEditor.currentSkin.data[index + 3] = 0;
                }
            }
        }
    }
    
    skinEditor.updateDisplay();
    skinEditor.showMessage(`Очищено ${skinEditor.selectedParts.size} частей`);
}

function selectMainLayer() {
    skinEditor.selectMainLayer();
}

function selectOverlayLayer() {
    skinEditor.selectOverlayLayer();
}

function clearSelection() {
    skinEditor.clearSelection();
}

function selectWorkMode(mode) {
    document.querySelectorAll('.mode-option').forEach(opt => opt.classList.remove('selected'));
    
    // Находим кнопку по режиму
    const buttons = document.querySelectorAll('.mode-option');
    buttons.forEach(btn => {
        if ((mode === 'skin' && btn.textContent.includes('Скин')) ||
            (mode === 'cape' && btn.textContent.includes('Плащ'))) {
            btn.classList.add('selected');
        }
    });
    
    skinEditor.workMode = mode;
    skinEditor.selectedParts.clear();
    skinEditor.createNewSkin();
    skinEditor.showMessage(`Переключен режим: ${mode === 'skin' ? 'Скин' : 'Плащ'}`);
}

function selectAllParts() {
    skinEditor.selectAllParts();
}

function selectMode(mode) {
    document.querySelectorAll('#parts .mode-option').forEach(opt => opt.classList.remove('selected'));
    
    // Находим кнопку по режиму в секции частей
    const buttons = document.querySelectorAll('#parts .mode-option');
    buttons.forEach(btn => {
        if ((mode === 'individual' && btn.textContent.includes('Отдельно')) ||
            (mode === 'stretch' && btn.textContent.includes('Растянуть'))) {
            btn.classList.add('selected');
        }
    });
    
    skinEditor.applyMode = mode;
}

function generate3DPreview() {
    skinEditor.generate3DPreview();
}

function rotatePreview() {
    skinEditor.rotatePreview();
}

function resetPreview() {
    skinEditor.resetPreview();
}

function toggleAnimation() {
    // Placeholder for animation toggle
    skinEditor.showMessage('Анимация пока не поддерживается');
}

function resetCamera() {
    skinEditor.resetPreview();
}