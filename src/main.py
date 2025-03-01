import customtkinter as ctk
from tkinter import filedialog, messagebox, colorchooser
from PIL import Image, ImageTk, ImageColor, ImageDraw
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import SquareModuleDrawer, GappedSquareModuleDrawer, CircleModuleDrawer, RoundedModuleDrawer
from qrcode.image.styles.colormasks import SolidFillColorMask

ctk.set_appearance_mode("System")

class SwiftQRApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("SwiftQR")
        self.geometry("1200x700")
        self.resizable(False, False)
        self.fill_color = "#000000"
        self.bg_color = "#FFFFFF"
        self.center_logo_path = None
        self.generated_image = None
        self.remove_logo_bg_var = ctk.BooleanVar(value=False)
        self.dark_theme_var = ctk.BooleanVar(value=(ctk.get_appearance_mode() == "Dark"))
        self.tabview = ctk.CTkTabview(self, width=1200, height=8000)
        self.tabview.pack(padx=20, pady=20, fill="both", expand=True)
        self.tabview.add("URL/Text")
        self.tabview.add("Settings")
        self.url_tab = self.tabview.tab("URL/Text")
        self.url_tab.grid_columnconfigure(0, weight=1)
        self.url_tab.grid_columnconfigure(1, weight=1)
        self.controls_frame = ctk.CTkFrame(self.url_tab)
        self.controls_frame.grid(row=0, column=0, padx=(10,5), pady=10, sticky="nsew")
        self.preview_frame = ctk.CTkFrame(self.url_tab)
        self.preview_frame.grid(row=0, column=1, padx=(5,10), pady=10, sticky="nsew")
        self.create_controls()
        self.create_preview_section()
        self.create_settings_tab()
        self.generate_qr()

    def create_controls(self):
        self.content_frame = ctk.CTkFrame(self.controls_frame, corner_radius=8)
        self.content_frame.pack(padx=10, pady=10, fill="x")
        self.content_label = ctk.CTkLabel(self.content_frame, text="Content (URL or text):", font=("Segoe UI", 16, "bold"))
        self.content_label.pack(padx=5, pady=5, anchor="w")
        self.content_entry = ctk.CTkEntry(self.content_frame, width=300)
        self.content_entry.pack(padx=5, pady=5, fill="x")
        self.customize_frame = ctk.CTkFrame(self.controls_frame, corner_radius=8)
        self.customize_frame.pack(padx=10, pady=10, fill="x")
        self.customize_label = ctk.CTkLabel(self.customize_frame, text="Customize QR", font=("Segoe UI", 16, "bold"))
        self.customize_label.pack(padx=5, pady=(5,10), anchor="w")
        self.fill_color_button = ctk.CTkButton(self.customize_frame, text=f"Fill Color: {self.fill_color}", command=self.choose_fill_color, width=150)
        self.fill_color_button.pack(padx=5, pady=5, anchor="w")
        self.bg_color_button = ctk.CTkButton(self.customize_frame, text=f"Background Color: {self.bg_color}", command=self.choose_bg_color, width=150)
        self.bg_color_button.pack(padx=5, pady=5, anchor="w")
        self.body_style_label = ctk.CTkLabel(self.customize_frame, text="Body Style:", font=("Segoe UI", 12, "bold"))
        self.body_style_label.pack(padx=5, pady=(10,0), anchor="w")
        self.body_style_combobox = ctk.CTkComboBox(self.customize_frame, values=["Square", "Gapped Square", "Circle", "Rounded"])
        self.body_style_combobox.set("Square")
        self.body_style_combobox.pack(padx=5, pady=5, anchor="w")
        self.logo_frame = ctk.CTkFrame(self.customize_frame, corner_radius=8)
        self.logo_frame.pack(padx=5, pady=10, fill="x")
        self.logo_frame_label = ctk.CTkLabel(self.logo_frame, text="Logo Options", font=("Segoe UI", 12, "bold"))
        self.logo_frame_label.pack(padx=5, pady=5, anchor="w")
        logo_button_frame = ctk.CTkFrame(self.logo_frame)
        logo_button_frame.pack(padx=10, pady=10)
        self.upload_logo_button = ctk.CTkButton(logo_button_frame, text="Upload Center Logo", command=self.upload_logo, font=("Segoe UI", 12, "bold"))
        self.upload_logo_button.pack(side="left", padx=5)
        self.remove_logo_button = ctk.CTkButton(logo_button_frame, text="Remove Logo", command=self.remove_logo, font=("Segoe UI", 12, "bold"))
        self.remove_logo_button.pack(side="left", padx=5)
        self.logo_filename_label = ctk.CTkLabel(self.logo_frame, text="No logo uploaded")
        self.logo_filename_label.pack(padx=5, pady=5, anchor="w")
        self.remove_qr_checkbox = ctk.CTkCheckBox(self.logo_frame, text="Remove QR behind logo", variable=self.remove_logo_bg_var, font=("Segoe UI", 12, "bold"))
        self.remove_qr_checkbox.pack(padx=5, pady=5, anchor="w")
        self.size_frame = ctk.CTkFrame(self.customize_frame, corner_radius=8)
        self.size_frame.pack(padx=5, pady=10, fill="x")
        self.size_label = ctk.CTkLabel(self.size_frame, text="Image Size (pixels):", font=("Segoe UI", 12, "bold"))
        self.size_label.pack(side="left", padx=5, pady=5)
        self.size_entry = ctk.CTkEntry(self.size_frame, width=100)
        self.size_entry.insert(0, "500")
        self.size_entry.pack(side="left", padx=5, pady=5)
        self.generate_button = ctk.CTkButton(self.controls_frame, text="Generate QR Code", command=self.generate_qr)
        self.generate_button.pack(padx=10, pady=10, fill="x")

    def create_preview_section(self):
        self.preview_section = ctk.CTkFrame(self.preview_frame, corner_radius=8)
        self.preview_section.pack(padx=10, pady=10, fill="both", expand=True)
        self.preview_heading = ctk.CTkLabel(self.preview_section, text="QR Code Preview", font=("Segoe UI", 16, "bold"))
        self.preview_heading.pack(padx=5, pady=5)
        self.preview_label = ctk.CTkLabel(self.preview_section, text="")
        self.preview_label.pack(padx=5, pady=5, expand=True)
        self.output_frame = ctk.CTkFrame(self.preview_frame, corner_radius=8)
        self.output_frame.pack(padx=10, pady=10, fill="x")
        self.output_label = ctk.CTkLabel(self.output_frame, text="Output Format:")
        self.output_label.pack(side="left", padx=5, pady=5)
        self.format_combobox = ctk.CTkComboBox(self.output_frame, values=["PNG", "JPG"])
        self.format_combobox.set("PNG")
        self.format_combobox.pack(side="left", padx=5, pady=5)
        self.save_button = ctk.CTkButton(self.preview_frame, text="Save QR Code", command=self.save_qr)
        self.save_button.pack(padx=10, pady=10, fill="x")

    def create_settings_tab(self):
        self.settings_frame = ctk.CTkFrame(self.tabview.tab("Settings"), corner_radius=8)
        self.settings_frame.pack(padx=20, pady=20, fill="both", expand=True)
        self.dark_theme_checkbox = ctk.CTkCheckBox(self.settings_frame, text="Enable Dark Theme", variable=self.dark_theme_var, command=self.toggle_dark_theme)
        self.dark_theme_checkbox.pack(padx=10, pady=10, anchor="w")

    def toggle_dark_theme(self):
        if self.dark_theme_checkbox.get():
            ctk.set_appearance_mode("Dark")
        else:
            ctk.set_appearance_mode("Light")

    def choose_fill_color(self):
        color = colorchooser.askcolor(title="Choose Fill Color")
        if color[1]:
            self.fill_color = color[1]
            self.fill_color_button.configure(text=f"Fill Color: {self.fill_color}", fg_color=self.fill_color)

    def choose_bg_color(self):
        color = colorchooser.askcolor(title="Choose Background Color")
        if color[1]:
            self.bg_color = color[1]
            self.bg_color_button.configure(text=f"Background Color: {self.bg_color}", fg_color=self.bg_color)

    def upload_logo(self):
        file_path = filedialog.askopenfilename(title="Select Logo Image", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")])
        if file_path:
            self.center_logo_path = file_path
            self.logo_filename_label.configure(text=file_path.split("/")[-1])

    def remove_logo(self):
        self.center_logo_path = None
        self.logo_filename_label.configure(text="No logo uploaded")

    def generate_qr(self):
        content = self.content_entry.get().strip() or "1"
        try:
            desired_size = int(self.size_entry.get())
        except ValueError:
            desired_size = 500
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=3)
        qr.add_data(content)
        qr.make(fit=True)
        matrix = qr.get_matrix()
        new_box_size = desired_size // (len(matrix) + 2 * qr.border)
        if new_box_size < 1:
            new_box_size = 1
        qr.box_size = new_box_size
        body_style = self.body_style_combobox.get()
        if body_style == "Square":
            module_drawer = SquareModuleDrawer()
        elif body_style == "Gapped Square":
            module_drawer = GappedSquareModuleDrawer()
        elif body_style == "Circle":
            module_drawer = CircleModuleDrawer()
        elif body_style == "Rounded":
            module_drawer = RoundedModuleDrawer()
        else:
            module_drawer = SquareModuleDrawer()
        img_kwargs = {"module_drawer": module_drawer, "color_mask": SolidFillColorMask(front_color=ImageColor.getrgb(self.fill_color), back_color=ImageColor.getrgb(self.bg_color))}
        img = qr.make_image(image_factory=StyledPilImage, **img_kwargs)
        pil_image = img.convert("RGB")
        if self.center_logo_path:
            try:
                logo = Image.open(self.center_logo_path)
                qr_width, qr_height = pil_image.size
                logo_size = int(qr_width * 0.2)
                pos = ((qr_width - logo_size) // 2, (qr_height - logo_size) // 2)
                if self.remove_logo_bg_var.get():
                    draw = ImageDraw.Draw(pil_image)
                    draw.rectangle((pos[0], pos[1], pos[0] + logo_size, pos[1] + logo_size), fill=self.bg_color)
                logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
                if logo.mode in ("RGBA", "LA"):
                    pil_image.paste(logo, pos, mask=logo)
                else:
                    pil_image.paste(logo, pos)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add logo: {e}")
        pil_image = pil_image.resize((desired_size, desired_size), Image.NEAREST)
        self.generated_image = pil_image
        preview = pil_image.copy()
        preview.thumbnail((400, 400))
        self.preview_photo = ImageTk.PhotoImage(preview)
        self.preview_label.configure(image=self.preview_photo)

    def save_qr(self):
        output_format = self.format_combobox.get()
        if not self.generated_image:
            messagebox.showerror("Error", "No QR code generated.")
            return
        if output_format == "PNG":
            filetypes = [("PNG files", "*.png")]
            default_ext = ".png"
        elif output_format == "JPG":
            filetypes = [("JPG files", "*.jpg")]
            default_ext = ".jpg"
        file_path = filedialog.asksaveasfilename(defaultextension=default_ext, filetypes=filetypes)
        if not file_path:
            return
        try:
            self.generated_image.save(file_path)
            messagebox.showinfo("Saved", f"QR code saved to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save QR code: {e}")

if __name__ == "__main__":
    SwiftQRApp().mainloop()
