-- Drop existing medicines table to reset
DROP TABLE IF EXISTS medicines;

-- Create medicines table with image_path column
CREATE TABLE IF NOT EXISTS medicines (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    stock INT NOT NULL,
    image_path VARCHAR(255) DEFAULT NULL
);

-- Insert 40 medicines with realistic Indian Rupee prices and image paths
INSERT INTO medicines (name, category, price, stock, image_path) VALUES
('Crocin', 'Pain Relief', 35.00, 200, 'crocin.jpg'),
('Dolo 650', 'Pain Relief', 30.00, 180, 'dolo_650.jpg'),
('Saridon', 'Pain Relief', 40.00, 150, 'saridon.jpg'),
('Combiflam', 'Pain Relief', 45.00, 160, 'combiflam.jpg'),
('Azithromycin', 'Antibiotic', 120.00, 100, 'azithromycin.jpg'),
('Cefixime', 'Antibiotic', 150.00, 90, 'cefixime.jpg'),
('Metrogyl', 'Antibiotic', 80.00, 120, 'metrogyl.jpg'),
('Glimepiride', 'Diabetes', 60.00, 110, 'glimepiride.jpg'),
('Rosuvastatin', 'Cholesterol', 90.00, 100, 'rosuvastatin.jpg'),
('Pantoprazole', 'Gastrointestinal', 50.00, 140, 'pantoprazole.jpg'),
('Domperidone', 'Gastrointestinal', 55.00, 130, 'domperidone.jpg'),
('Ventolin Inhaler', 'Respiratory', 280.00, 45, 'ventolin_inhaler.jpg'),
('Montelukast', 'Respiratory', 100.00, 80, 'montelukast.jpg'),
('Telmisartan', 'Hypertension', 70.00, 110, 'telmisartan.jpg'),
('Bisoprolol', 'Hypertension', 65.00, 100, 'bisoprolol.jpg'),
('Thyronorm', 'Thyroid', 90.00, 90, 'thyronorm.jpg'),
('Ecosprin', 'Anticoagulant', 20.00, 200, 'ecosprin.jpg'),
('Clopidogrel', 'Anticoagulant', 85.00, 95, 'clopidogrel.jpg'),
('Zoloft', 'Antidepressant', 110.00, 85, 'zoloft.jpg'),
('Alprazolam', 'Anxiolytic', 75.00, 70, 'alprazolam.jpg'),
('Vicks Action 500', 'Cold & Flu', 38.00, 150, 'vicks_action_500.jpg'),
('Sinarest', 'Cold & Flu', 42.00, 140, 'sinarest.jpg'),
('Calpol', 'Pain Relief', 32.00, 170, 'calpol.jpg'),
('Augmentin', 'Antibiotic', 180.00, 80, 'augmentin.jpg'),
('Ofloxacin', 'Antibiotic', 95.00, 100, 'ofloxacin.jpg'),
('Vildagliptin', 'Diabetes', 120.00, 90, 'vildagliptin.jpg'),
('Lipitor', 'Cholesterol', 100.00, 85, 'lipitor.jpg'),
('Rantac', 'Gastrointestinal', 25.00, 160, 'rantac.jpg'),
('Budecort Inhaler', 'Respiratory', 250.00, 50, 'budecort_inhaler.jpg'),
('Amlovas', 'Hypertension', 55.00, 120, 'amlovas.jpg'),
('Eltroxin', 'Thyroid', 85.00, 100, 'eltroxin.jpg'),
('Xarelto', 'Anticoagulant', 150.00, 70, 'xarelto.jpg'),
('Citalopram', 'Antidepressant', 90.00, 80, 'citalopram.jpg'),
('Lorazepam', 'Anxiolytic', 65.00, 60, 'lorazepam.jpg'),
('Zyrtec', 'Allergy', 45.00, 130, 'zyrtec.jpg'),
('Avil', 'Allergy', 30.00, 140, 'avil.jpg'),
('Digene', 'Antacid', 20.00, 200, 'digene.jpg'),
('Ciplox', 'Antibiotic', 110.00, 90, 'ciplox.jpg'),
('Teneligliptin', 'Diabetes', 80.00, 100, 'teneligliptin.jpg'),
('Otrivin', 'Nasal Decongestant', 35.00, 150, 'otrivin.jpg');