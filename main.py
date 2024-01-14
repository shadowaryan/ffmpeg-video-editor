import os
import sys
import pandas as pd
import subprocess


df = pd.read_csv('movie_list.csv')


def run_command(command):
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")

def get_audio_files(directory, file_extension):
    """
    Returns a list of paths to audio files with the specified extension in the given directory.
    """
    return [os.path.join(directory, file) for file in os.listdir(directory) if file.lower().endswith(file_extension)]

print(df['movie_list'].count())

def main():

    try:
        if len(sys.argv) > 0:
            claim_directory = sys.argv[1]
            movie_directory = sys.argv[2]
            export_directory = sys.argv[3]

            audio_files = get_audio_files(claim_directory, '.mp3')

            print(audio_files)
        
            for index, row in df.iterrows():
                # Step 1: Extract audio from the movie
                #ffmpeg -i movie.mkv -vn -q:a 0 -map a movie.mp3
                extracted_mp3_audio = (row["movie_list"]).split('.')[0]
                command = f'ffmpeg -i "{movie_directory}\{row["movie_list"]}" -vn -q:a 0 -map a "{export_directory}\exported_audio\{extracted_mp3_audio}.mp3" -y'
                # print(command+'\n')
                run_command(command)

                # Step 2: Prepare the movie audio for overlapping
                #second-minutes conversion
                #ffmpeg -i movie.mp3 -af "volume=enable='between(t,3000,3120)':volume=0, volume=enable='between(t,5400,5520)':volume=0, volume=enable='between(t,7200,7320)':volume=0, volume=enable='between(t,9000,9120)':volume=0" movie_silenced.mp3

                volume_enable = ''
                movie_silenced = row['movie_list'].split('.')[0] + '_silenced.mp3'

                for x in range(len(audio_files)):
                    volume_enable = volume_enable + f"volume=enable='between(t,{row[f'claim_{x}']*60},{(row[f'claim_{x}']*60)+120})':volume=0, "
                
                command_2 = f'''ffmpeg -i "{export_directory}\exported_audio\{extracted_mp3_audio}.mp3" -af "{volume_enable}" "{export_directory}\exported_audio\{movie_silenced}" -y'''
                run_command(command_2)
                # print(command_2+'\n')

                # Step 3: Overlap the additional audio files onto the movie audio
                #millisecond-minutes conversion
                # run_command(['ffmpeg', '-i', 'movie_silenced.mp3', '-i', 'input1.mp3', '-i', 'input2.mp3', '-i', 'input3.mp3', '-i', 'input4.mp3', '-filter_complex', "[1:a]adelay=3000000|3000000[aud1]; [2:a]adelay=5400000|5400000[aud2]; [3:a]adelay=7200000|7200000[aud3]; [4:a]adelay=9000000|9000000[aud4]; [0:a][aud1][aud2][aud3][aud4]amix=inputs=5:duration=first:dropout_transition=0", '-c:a', 'libmp3lame', 'output.mp3'])
                adelay = ''
                audio_input = ''
                aud = '[0:a]'
                for x in range(len(audio_files)):
                    adelay = adelay + f"[{x+1}:a]adelay={row[f'claim_{x}']*60000}|{row[f'claim_{x}']*60000}[aud{x+1}]; "
                    audio_input = audio_input + f'-i "{audio_files[x]}" '
                    aud = aud + f"[aud{x+1}]"
                
                movie_output_mp3 = f"{export_directory}\exported_audio\{row['movie_list'].split('.')[0]}_output.mp3"
                command_3 = f'''ffmpeg -i "{export_directory}\exported_audio\{movie_silenced}" {audio_input}-filter_complex "{adelay}{aud}amix=inputs={len(audio_files)+1}:duration=first:dropout_transition=0" -c:a libmp3lame "{movie_output_mp3}" -y'''

                run_command(command_3)
                # print(command_3+'\n')

                
                # Step 4: Combine the new audio with the video
                #run_command(['ffmpeg', '-i', 'movie.mp4', '-i', 'output.mp3', '-c:v', 'copy', '-map', '0:v:0', '-map', '1:a:0', '-shortest', 'final_movie.mp4'])
                movie_output = f"{export_directory}\{row['movie_list'].split('.')[0]}.mp4"
                command_4 = f'''ffmpeg -i "{movie_directory}\{row['movie_list']}" -i {movie_output_mp3} -c:v copy -map 0:v:0 -map 1:a:0 -shortest {movie_output} -y'''

                run_command(command_4)
                # print(command_4)
                
    except Exception as e:
        print(f"An error occurred: {e}")
        print('Please provide the correct number of arguments.\nuse command like this: python main.py <claim_directory> <movie_directory> <export_directory>')

if __name__ == "__main__":
    main()