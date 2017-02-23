# Installation

```
# Java for the pipeline applications that need it
sudo apt-get install openjdk-8-jdk
```

## Python and some libraries
We're using Python 3.5 and some libraries you need to install for `biocodices` to work:
```
# Ptyhon ternary for triangle plots
conda config --add channels conda-forge

conda install python=3.5
pip install -r requirements.txt

mkdir ~/.luigi

# Start Luigi server for the pipeline
luigid --pidfile ~/.luigi/pidfile --state-path ~/.luigi/statefile --logdir ~/.luigi/log
```

## Software and resources

Get these programs and install them:

<!-- * [FastQC](http://www.bioinformatics.babraham.ac.uk/projects/download.html) -->
* [ea-utils](https://code.google.com/archive/p/ea-utils/downloads)
* [GATk suite](https://www.broadinstitute.org/gatk/download/)
* [Picard Tools](https://github.com/broadinstitute/picard/releases/tag/2.3.0)
<!-- * [Samtools](https://sourceforge.net/projects/samtools/files/) -->
<!-- * [Vcftools](http://vcftools.sourceforge.net/downloads.html) -->
<!-- * [bcftools, tabix, htslib](http://www.htslib.org/download/) -->
<!-- * [Bedtools](https://github.com/arq5x/bedtools2/releases) -->
* [Variant Effect Predictor](http://www.ensembl.org/info/docs/tools/vep/script/vep_download.html)
    - Install with the INSTALL.pl script and download the cache for homo
      sapiens GRCh37.
* [SnpEff](http://snpeff.sourceforge.net/)

```bash
# Here I use ~/paip_resources as the location of the pipeline resources
mkdir -p ~/paip_resources/snpeff_data
mkdir -p ~/paip_resources/vep_data

# Download Snpeff human genome database:
java -jar /path/to/snpeff.jar \
    download GRCh37.70 \
    -datadir ~/paip_resources/snpeff_data

# Install VEP:
/path/to/VEP/INSTALL.pl \
    -c ~/paip_resources/vep_data \
    -d ~/paip_resources/vep_data \
    -s homo_sapiends_merged \
    -y GRCh37
```

You also need to download some resources from the web:

Browse GATK bundle ftp servers to get the reference genome. For the GRCh37 version, I ran this command: `wget ftp://gsapubftp-anonymous@ftp.broadinstitute.org/bundle/2.8/b37/human_g1k_v37.fasta.gz`. **Warning**: the decompressed file will weight ~3Gb.

Also from GATK servers, get files for known indels:

    - 1000 Genomes indels
    - Mills and 1000 Genomes Gold Standard
    - All known variants in GRCh37

```
wget ftp://gsapubftp-anonymous@ftp.broadinstitute.org/bundle/2.8/b37/1000G_phase1.indels.b37.vcf.gz
wget ftp://gsapubftp-anonymous@ftp.broadinstitute.org/bundle/2.8/b37/Mills_and_1000G_gold_standard.indels.b37.vcf.gz
wget ftp://gsapubftp-anonymous@ftp.broadinstitute.org/bundle/2.8/b37/dbsnp_138.b37.vcf.gz
```

Unzip all the GATK bundle files with a `gunzip <filename>` command.

Prepare the reference genome fasta for BWA and GATK use, as detailed [here](http://gatkforums.broadinstitute.org/gatk/discussion/1601/how-can-i-prepare-a-fasta-file-to-use-as-reference). You need the software installed in the first step for this:
```bash
/path/to/bwa index -a bwtsw human_g1k_v37.fasta
/path/to/samtools faidx human_g1k_v37.fasta
java -jar /path/to/picard.jar \
    CreateSequenceDictionary \
    REFERENCE=human_g1k_v37.fasta \
    OUTPUT=human_g1k_v37.dict
```

Finally, create a fasta file with the adapters to trim from your reads. I got the sequences from [Illumina's TruSeq documentation](http://support.illumina.com/content/dam/illumina-support/documents/documentation/chemistry_documentation/experiment-design/illumina-adapter-sequences_1000000002694-01.pdf). Make sure you create a valid fasta file ('>ID' in one line, sequence in the next one, repeat). The IDs don't really matter, the sequences will be read.

# Settings before running `paip`

`paip` will search for its config files in a `~/.paip` directory,
so create it with `mkdir -p ~/.paip`. You will also need an organized
resource folder, so I recommend creating a `~/paip/resources` directory:
`mkdir -p ~/biocodices/resources`. Put the resources you downloaded from the
web in there.

Create a `~/.biocodices/resources.yml` file where you will specify the base
directory you just created. In the yml add the filenames of the resources.
Mine looks like this:

```yaml
base_dir: /home/juan/paip_resources

illumina_adapters: illumina_adapters.fasta

reference_genome_hg19: &reference_genome_default human_g1k_v37.fasta
reference_genome: *reference_genome_default

reference_genome_hg19_dict: &reference_genome_default_dict human_g1k_v37.dict
reference_genome_dict: *reference_genome_default_dict

indels_1000G: 1000G_phase1.indels.b37.vcf
indels_mills: Mills_and_1000G_gold_standard.indels.b37.vcf

dbsnp_GRCh37: dbsnp_138.b37.vcf

ENPv1_variants: &ENPv1_variants ENPv1_variants.vcf
panel_variants: *ENPv1_variants

ENPv1_regions: &ENPv1_amplicons ENPv1_amplicons_sorted.bed
panel_regions: *ENPv1_amplicons

snpeff_datadir: snpeff_data
vep_datadir: vep_data
```

Create the settings file `~/.paip/executables.yml` with paths to every executable from the software you downloaded earlier. Avoid tildes (`~`), write whole paths. This is my file, for instance:

```yaml
fastq-mcf: /home/juan/software/ea-utils.1.1.2-537/fastq-mcf
bwa: /home/juan/software/bwa-0.7.15/bwa
picard: picard java -jar /home/juan/software/picard-tools-2.2.4/picard.jar
gatk: gatk java -jar /home/juan/software/GenomeAnalysisTK-3.7/GenomeAnalysisTK.jar
snpsift: java -jar /home/juan/software/snpEff_4.3i/SnpSift.jar
snpeff: java -jar /home/juan/software/snpEff_4.3i/snpEff.jar
vep: /home/juan/software/ensembl-tools-release-87/scripts/variant_effect_predictor/variant_effect_predictor.pl


```

# Recipes

## Feed `paip` with the input `fastq` files

Create a directory for a given sequencer run and create a `data` subdirectory
in it. Put the forward and reverse `fastq` files from all samples in `data`.
`biocodices` expects them to be named following this pattern:
`<sample_ID>.R1.fastq` for the forward reads, and `<sample_ID>.R2.fastq` for
the reverse reads of the same sample.

After putting the input `fastq` files in there, you're good to go!

## Variant calling

You can just call biocodices from the command line:

`<path_to_biocodices>/paip/pipeline/variant_calling <base_directory_of_sequencing>`

The directory you pass as argument should have a `data` subfolder with the R1 and R2 `fastq`s for each sample.

Otherwise, you can instantiate the `Sequencing` class and call variants for each of its samples. Each Sample object will take care of creating its own results directory
(named after the sample ID under the sequencing results directory). 

```python
# Instatiate a Sequencing object with the root dir of a sequencer run.
# The directory should have a 'data' subdir with the fastq files.
sequencing = Sequencing('~/MyProject/NGS0001')
samples = sequencing.samples()  # => A list of sample objects
sample = samples[0]
sample.reads_filenames()  # => The forward and reverse reads files

for sample in sequencing.samples():
    sample.call_variants()
```

The process will take some times (i.e. 5 mins per sample, YMMV) and each step
of the process will be logged to a different log file under the sample's result
directory. To check where that is, you can ask: `sample.results_dir`, but in
general results and logs will be stored in `<sequencing_dir>/results/<sample_dir>/`.
