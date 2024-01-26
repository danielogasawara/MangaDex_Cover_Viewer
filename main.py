from io import BytesIO
from tkinter import Entry, Frame, Tk, Label, Button, font
from requests import get as fetch
from PIL import Image, ImageTk
from requests.exceptions import RequestException
from json.decoder import JSONDecodeError


class Application(Tk):
    REQUEST_MANGA_URL = 'https://api.mangadex.org/manga/'
    REQUEST_MANGA_COVER_URL = 'https://api.mangadex.org/cover/'
    REQUEST_MANGA_COVER_DOWNLOAD = 'https://www.mangadex.org/covers/'

    def __init__(self):
        super().__init__()
        self.geometry('320x600')
        self.title('MangaDex - Cover Viewer')
        # Título da interface dentro
        self.app_title = Label(self, text='MagaDex Cover Viewer', font=font.Font(family='JetBrains_Mono', weight=font.BOLD),)
        self.app_title.pack(pady=20)
        # Frame de Pesquisa
        self.search_frame = Frame(self)
        self.search_frame_label_input = Label(self.search_frame,text='Insira o ID da obra')
        self.search_frame_label_input.grid(ipadx=0, row=0, column=0)
        self.search_frame_input = Entry(self.search_frame, width=40)
        self.search_frame_input.grid(row=1, column=0)
        self.search_frame_button = Button(self.search_frame,
                                          text='Buscar',
                                          width=10,
                                          command=self.search_manga)
        self.search_frame_button.grid(pady=15, row=2, column=0)
        self.search_frame.pack()
        # Separador
        self.divisao_horizontal = Frame(self, height=1, bg="gray")
        self.divisao_horizontal.pack(fill='x', padx=5, pady=5)
        # Versionamento
        self.appversion = Label(self, text='Versão 0.1')
        self.appversion.pack(side='bottom', pady=5)
        # Configurações da Janela
        self.resizable(width=False, height=False)

    def search_manga(self):
        try:
            manga_id = self.search_frame_input.get()
            manga_data = self.fetch_manga_data(manga_id)
            manga_cover_id = self.get_cover_art_id(manga_data)
            manga_cover_filename = self.fetch_cover_filename(manga_cover_id)
            self.display_manga_cover(manga_id, manga_cover_filename, manga_data)
        except (RequestException, JSONDecodeError) as e:
            print(f"Erro ao buscar dados do mangá: {e}")

    def fetch_manga_data(self, manga_id):
        res_manga = fetch(f'{self.REQUEST_MANGA_URL}{manga_id}')
        res_manga.raise_for_status() 
        return res_manga.json()

    def get_cover_art_id(self, manga_data):
        for item in manga_data['data']['relationships']:
            if item['type'] == 'cover_art':
                return item['id']
        raise ValueError("Nenhum cover_art encontrado nos dados do mangá")

    def fetch_cover_filename(self, cover_id):
        res_cover = fetch(f'{self.REQUEST_MANGA_COVER_URL}{cover_id}')
        res_cover.raise_for_status()
        return res_cover.json()['data']['attributes']['fileName']

    def display_manga_cover(self, manga_id, cover_filename, manga_data):
        manga_cover_image = fetch(f'{self.REQUEST_MANGA_COVER_DOWNLOAD}{manga_id}/{cover_filename}')
        downloaded_manga_cover = Image.open(BytesIO(manga_cover_image.content))
        resized_manga_cover = downloaded_manga_cover.resize([220, 320], Image.BICUBIC)
        self.manga_cover_photo = ImageTk.PhotoImage(resized_manga_cover)

        if hasattr(self, 'result_frame'):
            self.result_frame.destroy()

        self.result_frame = Frame(self)
        self.result_title = Label(self.result_frame, text=manga_data['data']['attributes']['title']['en'], font=font.Font(size=14, weight='bold'), wraplength=250)
        self.result_cover = Label(self.result_frame, image=self.manga_cover_photo)
        self.result_title.pack()
        self.result_cover.pack()
        self.result_frame.pack()

               
if __name__ == '__main__':
    app = Application()
    app.mainloop()
