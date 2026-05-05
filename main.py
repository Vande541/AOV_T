import sys
# Đánh lừa hệ thống để ép UnityPy dùng Python thuần, chống crash trên Termux
sys.modules['UnityPy.UnityPyBoost'] = None
sys.modules['UnityPyBoost'] = None

import os
import UnityPy_AOV
from PIL import Image
from UnityPy_AOV.enums import TextureFormat
from UnityPy_AOV.export.MeshRendererExporter import export_mesh_renderer

# ... (Toàn bộ phần code xuất nhập của bạn ở dưới giữ nguyên không cần đổi gì cả)


def export_assets(input_folder):
    # Tạo cả 2 thư mục gốc chứa Texture và Mesh
    texture_root = os.path.join(input_folder, "Texture2D")
    mesh_root = os.path.join(input_folder, "Mesh")
    os.makedirs(texture_root, exist_ok=True)
    os.makedirs(mesh_root, exist_ok=True)

    for file in os.listdir(input_folder):
        if file.endswith(".assetbundle"):
            bundle_path = os.path.join(input_folder, file)
            env = UnityPy_AOV.load(bundle_path)
            
            # Tạo thư mục con cho từng assetbundle
            texture_folder = os.path.join(texture_root, os.path.splitext(file)[0])
            mesh_folder = os.path.join(mesh_root, os.path.splitext(file)[0])
            os.makedirs(texture_folder, exist_ok=True)
            os.makedirs(mesh_folder, exist_ok=True)
            
            missing_assets = []

            for obj in env.objects:
                # ==========================================
                # 1. TRÍCH XUẤT TEXTURE 2D (Đơn lẻ)
                # ==========================================
                if obj.type.name == "Texture2D":
                    try:
                        data = obj.read()
                        dest = os.path.join(texture_folder, f"{data.m_Name}")
                        img = data.image.convert("RGBA")
                        img.save(dest + ".png")
                        print(f"✅ Đã xuất Texture: {data.m_Name}")
                    except Exception as e:
                        print(f"❌ Lỗi khi xuất Texture {getattr(data, 'm_Name', obj.path_id)}: {e}")
                        missing_assets.append(f"Texture_{obj.path_id}")

                # ==========================================
                # 2. TRÍCH XUẤT MODEL HOÀN CHỈNH (Khuyên dùng)
                # ==========================================
                elif obj.type.name in ["SkinnedMeshRenderer", "MeshRenderer"]:
                    try:
                        # Dùng hàm của thư viện custom để xuất cả obj, mtl và texture đi kèm
                        export_mesh_renderer(obj, mesh_folder)
                        print(f"✅ Đã xuất Model hoàn chỉnh từ: {obj.type.name} (PathID: {obj.path_id})")
                    except Exception as e:
                        print(f"❌ Lỗi khi xuất Model {obj.type.name} (PathID: {obj.path_id}): {e}")
                        missing_assets.append(f"Model_{obj.path_id}")

                # ==========================================
                # 3. TRÍCH XUẤT MESH THÔ (Dự phòng)
                # ==========================================
                elif obj.type.name == "Mesh":
                    try:
                        data = obj.read()
                        mesh_name = getattr(data, "name", f"Mesh_{obj.path_id}")
                        dest = os.path.join(mesh_folder, f"{mesh_name}.obj")
                        
                        with open(dest, "wt", encoding="utf8", newline="") as f:
                            f.write(data.export())
                        print(f"✅ Đã xuất Mesh thô: {mesh_name}")
                    except Exception as e:
                        print(f"❌ Lỗi khi xuất Mesh (PathID: {obj.path_id}): {e}")
                        missing_assets.append(f"Mesh_{obj.path_id}")

            print(f"Tổng số asset bị lỗi trong {file}: {len(missing_assets)}")
            
            if missing_assets:
                print(f"Danh sách asset lỗi: {missing_assets}")
            print(f"Đã xuất xong dữ liệu từ {file}\n" + "-"*30)

def import_textures(input_folder):
    for file in os.listdir(input_folder):
        if file.endswith(".assetbundle"):
            bundle_path = os.path.join(input_folder, file)
            env = UnityPy_AOV.load(bundle_path)
            texture_folder = os.path.join(input_folder, "Texture2D", os.path.splitext(file)[0])

            if not os.path.exists(texture_folder):
                print(f"❌ Không tìm thấy thư mục {texture_folder}. Hãy chắc chắn rằng đã xuất ảnh trước!")
                continue

            for obj in env.objects:
                if obj.type.name == "Texture2D":
                    try:
                        data = obj.read()
                        fp = os.path.join(texture_folder, f"{data.m_Name}.png")
                        if os.path.exists(fp):
                            pil_img = Image.open(fp).convert("RGBA")
                            data.set_image(pil_img, TextureFormat.RGBA32)
                            data.save()
                            print(f"✅ Đã nhập: {data.m_Name}")
                                
                        else:
                            print(f"Không tìm thấy {fp}, bỏ qua.")
                    except Exception as e:
                        print(f"❌ Lỗi khi nhập {data.m_Name}: {e}")
                        
            output_bundle = os.path.join(input_folder, f"{os.path.splitext(file)[0]}_mod.assetbundle")
            with open(output_bundle, "wb") as f:
                f.write(env.file.save("lz4"))

            print(f"Đã nhập ảnh vào {output_bundle}")

def main():
    input_folder = input("📂 Nhập thư mục: ").strip()
    
    if not os.path.exists(input_folder):
        print("❌ Thư mục không tồn tại!")
        return
    
    print("\n1️⃣ Extract Texture2D & Mesh")
    print("2️⃣ Import Texture2D")
    
    mode = input("👉 Chọn: ").strip()
    
    if mode == "1":
        export_assets(input_folder)
    elif mode == "2":
        import_textures(input_folder)
    else:
        print("❌ Lựa chọn không hợp lệ!")

if __name__ == "__main__":
    main()
