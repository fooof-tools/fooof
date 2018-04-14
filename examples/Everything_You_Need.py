import numpy as np
import matplotlib.pyplot as plt
from fooof import FOOOF
from fooof import FOOOFGroup
from fooof.plts.templates import plot_spectrum

"""Variables"""

"""the path below is where you can put folders for each brain region and one
 for the raw data files to be accessed. Within each brain region folder, 
 create 2 folders such as the following: Child_OAReports and ChildFlatSpecs_OA
 ie.
 Raw data folder: /Users/userx/fooof/tutorial/dat/raw_Childdata
 group parameters/reports: /Users/userx/fooof/tutorial/dat/ChildResults_OA/
 individual reports: /Users/userx/fooof/tutorial/dat/ChildResults_OA/Child_OAReports
 individual flattened reports: /Users/userx/fooof/tutorial/dat/ChildResults_OA/ChildFlatSpecsOA"""
 
base_params_save_path= '/Users/userx/fooof/tutorial/dat/'

patient_group= 'Child'
brain_region= 'OA'
number_of_patients = 98

"""put the following files in a folder titled as such: raw_Childdata """
 
frequencies_file_name= 'FrequenciesChild.txt'
power_file_name= 'Occipital_Absolute_Power.txt'

"""parameters"""

freq_range = [0, 60] 
peak_width_limits=[1.5, 8]
max_n_peaks=6
min_peak_amplitude=0.3
peak_threshold=2.0

"""can add peak_threshold and knee below"""

fm= FOOOF(peak_width_limits, max_n_peaks , min_peak_amplitude)
fg = FOOOFGroup(peak_width_limits, max_n_peaks, min_peak_amplitude, peak_threshold) #, background_mode='knee')

def get_group_results(fg, frequencies, spectrum, freq_range, params_save_path):
    fg.fit(frequencies, spectrum)
    fg.report(frequencies, spectrum, freq_range)
    joiner= [patient_group, '_Group_results', brain_region]
    file_name= ''.join(joiner) #make sure to rename, or delete old file when running again
    file_path= params_save_path
    fg.save_report(file_name,file_path) #saves entire report  
    fg.print_results()
    fg.plot()

def get_data_for_each_fit(fg, params_save_path, patient_group, brain_region):
    
    """outputs text files with important data on the model fits"""
    
    bgps = fg.get_all_data('background_params')
    # Extract peak data
    cfs = fg.get_all_data('peak_params', 'CF')
    # Extract metadata about the model fit
    errors = fg.get_all_data('error')
    r2s = fg.get_all_data('r_squared')
    joiner= [params_save_path, 'Back_Params', patient_group, brain_region, '.txt']
    np.savetxt(''.join(joiner), np.array(bgps))
    joiner= [params_save_path, 'error', patient_group, brain_region, '.txt']
    np.savetxt(''.join(joiner), np.array(errors))
    joiner= [params_save_path, 'r_squared', patient_group, brain_region, '.txt']
    np.savetxt(''.join(joiner), np.array(r2s))
    joiner= [params_save_path, 'indexed_peaks', patient_group, brain_region, '.txt']
    np.savetxt(''.join(joiner), np.array(cfs))

def get_individual_fits(number_of_patients, patient_group, brain_region, fg, params_save_path):
        for i in range (0, number_of_patients):
            fm = fg.get_fooof(ind=i, regenerate=True) # Extract a particular spectrum, specified by index to a FOOOF object
            joiner= [patient_group, '_', brain_region, 'patient']
            to_string= [''.join(joiner), i+1]
            string_to_name= ''.join(str(e) for e in to_string)
            file_name=''.join(string_to_name)
            joiner= [params_save_path, patient_group, '_', brain_region, 'Reports/']
            file_path=''.join(joiner)
            fm.save_report(file_name,file_path)

"""flattened plots can be useful for the initial phase of locating peaks and choosing the best parameters"""

def get_flattened_plots(spectrum, frequencies, number_of_patients, fm, fg, patient_group, brain_region, params_save_path):
    freqs= frequencies
    doge= spectrum
    plt_log = False
    for n in range (0, number_of_patients):
        spectrum= doge[n]
        fm.add_data(freqs, spectrum, [0, 60])
        print (fm._spectrum_flat)
        plot_spectrum(freqs, spectrum, plt_log, label='Flattened Spectrum1')
        fm.fit(freqs, spectrum, [0, 60])
        plot_spectrum(fm.freqs, fm._spectrum_flat, plt_log, label='Flattened Spectrum')
        joiner= [params_save_path, patient_group, 'FlatSpecs_', brain_region, '/', patient_group, 'FlatSpec_', brain_region]
        to_string= [''.join(joiner), n+1]
        string_to_name= ''.join(str(e) for e in to_string)
        plt.savefig(string_to_name)
        plt.close(string_to_name)
        
        
def run_fooofgroup(number_of_patients, base_params_save_path, patient_group, brain_region, freq_range):

    """converts text files of Power and Frequency to numpy files to be processed by FOOOFGroup
    """
    
    joiner= [base_params_save_path, patient_group, 'Results_', brain_region, '/']
    params_save_path= ''.join(str(e) for e in joiner)
    
    fm= FOOOF(peak_width_limits=[1.5, 8], max_n_peaks=6 , min_peak_amplitude=0.3)
    
    joiner= [base_params_save_path, 'raw_', patient_group, 'data/', frequencies_file_name]
    
    """remove hashtags before ", delimiter" for text files with comma-separated data points"""
    
    realfreqs = np.loadtxt(''.join(joiner)) #, delimiter = ',', usecols=range((118)))
    
    
    joiner= [base_params_save_path, 'raw_', patient_group, 'data/', power_file_name]
    realspectrum = np.loadtxt(''.join(joiner)) #,delimiter = ',', usecols=range((118)))
    joiner= [base_params_save_path, patient_group, 'Results_', brain_region, '/Freqs_', brain_region, '_', patient_group, '.npy']
    np.save(''.join(joiner), np.array(realfreqs)) 
    joiner= [base_params_save_path, patient_group, 'Results_', brain_region, '/Freqs_', brain_region, '_', patient_group, '.npy']
    frequencies = np.load(''.join(joiner)) #load new freqlist
    joiner= [params_save_path, 'Spec_', brain_region, '_', patient_group, '.npy']
    np.save(''.join(joiner), np.array(realspectrum)) 
    joiner= [params_save_path, 'Spec_', brain_region, '_', patient_group, '.npy']
    spectrum = np.load(''.join(joiner)) #load new powlist
    
    """flattens, to pdfs"""
    
    get_flattened_plots(spectrum, frequencies, number_of_patients, fm, fg, patient_group, brain_region, params_save_path)
    
    """group results, to pdf"""
    
    get_group_results(fg, frequencies, spectrum, freq_range, params_save_path)
    
    """Extract background data, to pdfs"""
    
    get_data_for_each_fit(fg, params_save_path, patient_group, brain_region)
    
    """saves individual fits, to pdfs!"""
    
    get_individual_fits(number_of_patients, patient_group, brain_region, fg, params_save_path)



run_fooofgroup(number_of_patients, base_params_save_path, patient_group, brain_region, freq_range)
