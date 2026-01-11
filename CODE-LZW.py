import tkinter as tk  # Thư viện chính để tạo GUI
from tkinter import ttk, scrolledtext, messagebox  # Các widget con: Notebook (tab), ScrolledText (hộp văn bản cuộn), Messagebox (hộp thoại lỗi)
from PIL import Image, ImageTk  # Thư viện Pillow để xử lý ảnh (logo)


# --- 1. HÀM MÃ HÓA (ENCODE) ---
def encode_lzw(data):
    if not data:  # Kiểm tra nếu data rỗng
        return [], {}, 0.0  # Trả về rỗng
    # Khởi tạo từ điển: Map các ký tự ASCII (0-255) thành mã số tương ứng
    dictionary = {chr(i): i for i in range(256)} #chr(i): Chuyển số i thành ký tự ASCII (ví dụ: chr(65) = 'A').
    next_code = 256  # Mã tiếp theo bắt đầu từ 256
    # Bước 1 & 2: Tìm chuỗi dài nhất trong từ điển
    result = []
    prefix = ""
    for char in data:  # Duyệt từng ký tự trong chuỗi input
        word = prefix + char

        # tìm chuỗi chưa xuất hiện  trong tư điển
        if word in dictionary:
            prefix = word  # Tiếp tục tìm chuỗi dài hơn)
        else:
            # Bước 3: Ghi mã của chuuỗi đã  biết  vào kết quả
            result.append(dictionary[prefix])
            dictionary[word] = next_code
            next_code += 1  # Tăng mã mới cho lần sau

            # Bước 4: Đặt prefix là ký tự hiện tại, bắt đầu chuỗi mới
            prefix = char

    # Bước cuối: Ghi mã của prefix cuối cùng vào kết quả (nếu còn dư)
    if prefix:
        result.append(dictionary[prefix])

    # Tính tỷ số nén (CR)
    # Kích thước gốc: Số ký tự nhân 8 bits (ASCII 8-bit)
    # Kích thước nén: Số mã nhân 9 bits
    original_size = len(data) * 8  # bits
    compressed_size = len(result) * 9  # bits
    compression_ratio = compressed_size / original_size if original_size > 0 else 0.0  # CR <1: tốt

    return result, dictionary, compression_ratio


# --- 2. HÀM GIẢI MÃ (DECODE) ---
def decode_lzw(code):
    """Thực hiện giải mã LZW trên list các mã (int) đã nén."""
    if not code:
        return ""   # Trả về chuỗi rỗng

    # Khởi tạo từ điển: Map các mã (0-255) thành ký tự ASCII
    dictionary = {i: chr(i) for i in range(256)}
    next_code = 256  # Mã mới bắt đầu từ 256

    # Lấy mã đầu tiên và tìm chuỗi tương ứng
    old_code = code[0]
    output_string = dictionary[old_code]
    prefix = output_string  #lưu giá trị này làm prefix ban đầu cho vòng lặp sau

    # Duyệt qua các mã còn lại (từ mã thứ 2)
    for new_code in code[1:]:

        if new_code in dictionary:  # Nếu mã đã có trong từ điển thì  lấy value bằng  chỗi trong từ điển
            value = dictionary[new_code]
        else:
            # Mã chưa có trong từ điển (Trường hợp "chuỗi + ký tự đầu tiên của chuỗi")
            if new_code == next_code:
                value = prefix + prefix[0]
            else:
                # Xử lý lỗi nếu mã không hợp lệ (nên không xảy ra trong LZW chuẩn)
                raise ValueError("Bad code in decoded stream")

        # In chuỗi giải mã
        output_string += value
        # Cập nhật từ điển Chuỗi mới = prefix + ký tự đầu tiên của chuỗi hiện tại
        word = prefix + value[0]
        dictionary[next_code] = word  # Thêm chuỗi mới vào từ điển
        next_code += 1  # Tăng mã mới
        # Cập nhật prefix cho lần lặp tiếp theo
        prefix = value
    return output_string  # Trả về chuỗi đầy đủ


# --- 3. HÀM ĐÁNH GIÁ TỶ SỐ NÉN ---
def evaluate_compression(ratio):
    """Đánh giá tỷ số nén (CR).
    - CR < 1: Nén tốt (kích thước nén nhỏ hơn gốc).
    - CR = 1: Không thay đổi.
    - CR > 1: Nén xấu (kích thước nén lớn hơn).
    """
    if ratio < 1:
        return "Có nén (tốt)"
    elif ratio == 1:
        return "Không nén được"
    else:
        return "Dữ liệu sau nén lớn hơn (trường hợp xấu)"

# --- 4. HÀM HỖ TRỢ CHO TAB MÃ HÓA, Thực hiện mã hóa, input, tính phần trăM,,,, ---
def perform_encode():

    try:
        data_in = encode_entry.get().upper()  # Chuyển sang chữ hoa để đơn giản hóa từ điển (tránh phân biệt hoa/thường)
        if not data_in:  # Kiểm tra input rỗng
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập chuỗi dữ liệu.")  # Hộp thoại cảnh báo
            return  # Dừng hàm
        compressed_codes, _, compression_ratio = encode_lzw(data_in)  # Gọi hàm encode, lấy mã và CR

        # Tính kích thước của chuỗi kí tự đã mã hóa và giải mã
        original_size = len(data_in) * 8
        compressed_size = len(compressed_codes) * 9
        # Phần trăm tiết kiệm = (1 - CR) * 100%
        savings_percent = (1 - compression_ratio) * 100 if original_size > 0 else 0.0

        # Giải mã ngay lập tức để kiểm tra
        decompressed_data = decode_lzw(compressed_codes)
        verification = "Khớp hoàn toàn" if decompressed_data == data_in else "Không khớp (lỗi)"

        # Xây dựng text kết quả
        result_text = f"Chuỗi Gốc: {data_in}\n"
        result_text += f"Kết quả Encode (dãy mã): {compressed_codes}\n\n"

        # Thêm thông tin tỷ số nén và tiết kiệm
        result_text += f"Tỷ số nén: {compression_ratio:.3f}\n"  # Hiển thị CR với 2 chữ số thập phân
        result_text += f"Phần trăm tiết kiệm: {savings_percent:.3f}%\n"
        result_text += f"Đánh giá: {evaluate_compression(compression_ratio)}\n\n"

        # Thêm phần giải mã ngay
        result_text += "--- PHẦN GIẢI MÃ TỰ ĐỘNG ---\n"
        result_text += f"Dãy mã để giải mã: {compressed_codes}\n"
        result_text += f"Kết quả Decode: {decompressed_data}\n"
        result_text += f"Xác thực: {verification}"

        # Xóa  kết quả cũ, hiển thị kết quả mới
        encode_output.delete(1.0, tk.END)  # Xóa từ đầu đến cuối
        encode_output.insert(tk.END, result_text)
    except Exception as e:
        messagebox.showerror("Lỗi", f"Đã xảy ra lỗi: {e}")  # Hộp thoại lỗi


# --- 5. HÀM HỖ TRỢ CHO TAB GIẢI MÃ --
def perform_decode():

    try:
        code_str = decode_entry.get()  # Lấy chuỗi mã từ Entry
        if not code_str:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập dãy mã.")
            return
        # Parse chuỗi mã thành list int (cách nhau bằng space)
        codes = [int(x) for x in code_str.split()]
        decompressed_data = decode_lzw(codes)  # Gọi hàm decode
        # Xây dựng text kết quả
        result_text = f"Dãy Mã Nhập: {code_str}\n"
        result_text += f"Kết quả Decode: {decompressed_data}"

        # Xóa cũ và chèn mới
        decode_output.delete(1.0, tk.END)
        decode_output.insert(tk.END, result_text)
    except ValueError:  # Lỗi parse int (mã không phải số)
        messagebox.showerror("Lỗi", "Dữ liệu nhập vào không hợp lệ. Vui lòng nhập dãy số nguyên.")
    except Exception as e:  # Lỗi chung
        messagebox.showerror("Lỗi", f"Đã xảy ra lỗi: {e}")


def on_exit():
    root.quit()  # Thoát vòng lặp mainloop




# --- 6. GIAO DIỆN CHÍNH ---
root = tk.Tk()  # Tạo cửa sổ chính (root window)
root.title("Dictionary Coding (LZW)")  # Đặt  tên
root.geometry("600x550")  # Đặt kích thước giao diện

# ---  HÀM THÊM LOGO ---
def add_logo():
    try:
        logo_img = Image.open(r"D:\XuLyAnh\APP\PythonProject2\logolzw.jpg")
        logo_img = logo_img.resize((150, 150))  # chỉnh kích thước của logo  lại
        logo_tk = ImageTk.PhotoImage(logo_img)  # Chuyển PIL Image thành Tkinter PhotoImage
        logo_label = tk.Label(root, image=logo_tk, bg="white")
        logo_label.pack(pady=10)  # Đặt vào cửa sổ với khoảng cách trên/dưới 10px
        root.logo_tk = logo_tk
    except FileNotFoundError:  # Nếu file không tồn tại
        # Hiển thị thông báo lỗi thay vì logo
        tk.Label(root, text="Logo không tìm thấy (logo.png)", fg="red").pack(pady=10)
    except Exception as e:
        messagebox.showerror("Lỗi Logo", f"Không thể tải logo: {e}")
# Thêm logo trước tiêu đề (gọi hàm)
add_logo()

# Tiêu đề chính (Label lớn)
title_label = tk.Label(root, text="DICTIONARY CODING (LZW)", font=("Arial", 16, "bold"))
title_label.pack(pady=10)  # Đặt vào root với khoảng cách trên/dưới 10px
notebook = ttk.Notebook(root)  # Tạo Notebook từ ttk (hiện đại hơn tk)
notebook.pack(expand=True, fill='both', padx=10, pady=10)  # Đặt vào root, mở rộng theo kích thước, padding 10px

# Tab 1: Mã Hóa
encode_frame = ttk.Frame(notebook)  # Frame chứa nội dung tab
notebook.add(encode_frame, text="1. Mã Hóa")  # Thêm tab với tên

tk.Label(encode_frame, text="Nhập chuỗi dữ liệu:").pack(pady=5)  # Label hướng dẫn, padding 5px
encode_entry = tk.Entry(encode_frame, width=50)  # Ô nhập text (rộng 50 ký tự)
encode_entry.pack(pady=5)  # Đặt với padding

tk.Button(encode_frame, text="Mã Hóa", command=perform_encode, width=15, height=1).pack(pady=10)
# Nút bấm, gọi hàm perform_encode khi click, kích thước 15x1

tk.Label(encode_frame, text="Kết quả:").pack(pady=5)  # Label cho output
encode_output = scrolledtext.ScrolledText(encode_frame, wrap=tk.WORD, width=70, height=15)
# Hộp text cuộn, wrap theo từ, kích thước 70x15
encode_output.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)  # Mở rộng theo frame

# Tab 2: Giải Mã (tương tự tab 1)
decode_frame = ttk.Frame(notebook)
notebook.add(decode_frame, text="2. Giải Mã")

tk.Label(decode_frame, text="Nhập dãy mã (cách nhau bằng dấu cách, ví dụ: 65 66 256 256):").pack(pady=5)
decode_entry = tk.Entry(decode_frame, width=50)
decode_entry.pack(pady=5)

tk.Button(decode_frame, text="Giải Mã", command=perform_decode, width=15, height=1).pack(pady=10)

tk.Label(decode_frame, text="Kết quả:").pack(pady=5)
decode_output = scrolledtext.ScrolledText(decode_frame, wrap=tk.WORD, width=70, height=15)
decode_output.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Nút Thoát ở dưới cùng (ngoài tab, ở root)
tk.Button(root, text="3. Thoát", command=on_exit, width=15, height=1).pack(pady=10)

# Chạy ứng dụng: Bắt đầu vòng lặp sự kiện Tkinter (hiển thị cửa sổ và lắng nghe sự kiện)
if __name__ == "__main__":
    root.mainloop()  # Chạy mainloop cho đến khi thoát