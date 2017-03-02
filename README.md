# Installation

```
# Java for the pipeline applications that need it
sudo apt-get install openjdk-8-jdk
```

## Python and some libraries
You need a working Python 3.5 or greater installation.
[Anaconda](https://www.continuum.io/downloads) is an easy way to get it.

Then you can install `paip`:

```bash
# cd to paip directory and run:
pip install -r requirements.txt
python setup.py install  # This will make the paip command available

# Now you should be able to run paip
paip --help
```

## Software

Grab the software in `paip/software` and install it in your system (the instructions
vary for each program, check their READMEs). These are the programs that will
be used during the pipeline.

SnpEff and VEP need some special steps to prepare local annotation databases.
I will use `~/paip_resources` as the resources folder throught this guide,
but you can choose any other path:

```bash
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

## Resources

You also need to download some resources from the web. Browse GATK bundle ftp
servers to get the reference genome. For the GRCh37 version, I ran this command:

```bash
wget ftp://gsapubftp-anonymous@ftp.broadinstitute.org/bundle/2.8/b37/human_g1k_v37.fasta.gz
```

**Warning**: the decompressed file will weigh ~3Gb.

Also from GATK servers, get files for known indels:

    - 1000 Genomes indels (VCF)
    - Mills and 1000 Genomes Gold Standard (VCF)
    - dbSNP variants in GRCh37 (VCF)

```bash
wget ftp://gsapubftp-anonymous@ftp.broadinstitute.org/bundle/2.8/b37/1000G_phase1.indels.b37.vcf.gz
wget ftp://gsapubftp-anonymous@ftp.broadinstitute.org/bundle/2.8/b37/Mills_and_1000G_gold_standard.indels.b37.vcf.gz
wget ftp://gsapubftp-anonymous@ftp.broadinstitute.org/bundle/2.8/b37/dbsnp_138.b37.vcf.gz
```

Grab also the *Homo sapiens* GTF file from Ensembl:

```bash
wget ftp://ftp.ensembl.org/pub/grch37/release-87/gtf/homo_sapiens/Homo_sapiens.GRCh37.87.gtf.gz
```

Unzip all the `.gz` files with a `gunzip <filename>` command.

Prepare the reference genome fasta for BWA and GATK use, as detailed [here](http://gatkforums.broadinstitute.org/gatk/discussion/1601/how-can-i-prepare-a-fasta-file-to-use-as-reference). You need the software installed in the previous step for this:
```bash
/path/to/bwa index -a bwtsw human_g1k_v37.fasta
/path/to/samtools faidx human_g1k_v37.fasta
java -jar /path/to/picard.jar \
    CreateSequenceDictionary \
    REFERENCE=human_g1k_v37.fasta \
    OUTPUT=human_g1k_v37.dict
```

Prepare the SnpEff installation downloading the Homo Sapiens GRCh37 database,
and the VEP installation for the same assembly:

```bash
# In both cases, choose the path to your resources dir

/path/to/snpeff download GRCh37.75 -v -datadir ~/paip_resources/snpeff_data

/path/to/VEP/INSTALL.pl -d ~/paip_resources/vep_data -c ~/paip_resources/vep_data -s homo_sapiends_merged -y GRCh37
```

Finally, create a fasta file with the adapters to trim from your reads. I got the sequences from [Illumina's TruSeq documentation](http://support.illumina.com/content/dam/illumina-support/documents/documentation/chemistry_documentation/experiment-design/illumina-adapter-sequences_1000000002694-01.pdf). Make sure you create a valid fasta file ('>ID' in one line, sequence in the next one, repeat)

# Settings before running `paip`

`paip` will search for its config files in a `~/.paip` directory,
so create it with `mkdir -p ~/.paip`. You will also need a
directory for the resources. I recommend locating it at `~/paip_resources`:
`mkdir -p ~/paip_resources`. Put the resources you downloaded from the
web in there.

Create a `~/.paip/resources.yml` with the path to the resources directory and 
the filenames of the resources. Use a comple filepath, no tilde `~`. I recommend
using the example YAML at `example_config/resources.yml` as a guide.

Create also the file `~/.paip/executables.yml` with paths to every executable
needed in the pipeline. Avoid tildes (`~`) again. You can use `example_config/executables.yml`
as a guide.

Finally, you can copy the `example_config/commands.yml` file to your `~/.paip`
folder. The exact commands run in each step are specified there, and you might
want to tune them for your needs.

# Recipes

## Feed `paip` with the input `fastq` files

Create a directory for a given sequencer run with a subdirectory
for each sample, where the `fastq` files will be put, and a `sequencing_data.yml`
file with data about the samples. It will look like this:

```
Sequencing1
|
|—— sequencing_data.yml
|
|—— Sample1
|   |—— Sample1.R1.fastq
|   |—— Sample1.R2.fastq
|
|—— Sample2
|   |—— Sample2.R1.fastq
|   |—— Sample2.R2.fastq
|
...
```

The filenames for forward and reverse reads are expected to have this format:
`<sample_ID>.R1.fastq` and `<sample_ID>.R2.fastq`. It's important that the
sample IDs in the filenames are found in the `sequencing_data.yml` file, whose
structure will be like this:

```
Sample1:
  library_id: Lib1
  sequencing_id: Seq1
  id_in_sequencing: Sample1
  platform: Illumina
  platform_unit: IlluminaPU

Sample2:
  library_id: Lib1
  sequencing_id: Seq1
  id_in_sequencing: Sample2
  platform: Illumina
  platform_unit: IlluminaPU
```

I recommend keeping the `id_in_sequencing` the same as the sample ID,
because the read groups and the VCF will use the former, while the filenames
will use the latter, so different sample names might lead to confusion.

Only samples that are found in `sequencing_data.yml` will be seen by
the pipeline.

## Variant calling

To run any tasks you need a `luigi` server running. I use this simple setting:

```bash
mkdir -p ~/.luigi

luigid --pidfile ~/.luigi/pidfile --state-path ~/.luigi/statefile --logdir ~/.luigi/log
```

You can run it in background mode with `--background`. Once the server is running,
you can call `paip` from the command line:

```bash
paip VariantCalling --basedir /path/to/Sequencing1
```

The tree of dependencies will be built and start running. `luigi` provides a
nice web interface at `http://localhost:8082`.

There are three `--pipeline-type` options for the variant calling:
`variant_sites` (default), `target_sites`, `all_sites`. The `target_sites`
option needs a VCF resource file with the exact sites that will be
variant called, to be found under the key `panel_variants` in the resources
YAML.

The variant calling can also be run for a subset of the samples by specifying
something like `--samples Sample1,Sample4,Sample10` in the command line.

Finally, `luigi` options will also work. You can run with `--workers 2` to have
to simultaneous processes running the pipeline, but keep an eye on the RAM,
specially during the `AlignToReference` task.

## Quality Control

After the variant calling is done, you can optionally run a quality control
over its results:

```bash
paip QualityControl --basedir /path/to/Sequencing1
```

The result of the QC will be an HTML report generated by `multiqc`.

## Running tasks separately

Any task can be run separately. Some of them are sample tasks, like
`AlignToReference`, so they need a `--sample` parameter:

```bash
paip AlignToReference --sample Sample1 --basedir /path/to/Sequencing1
```

`luigi` will take care of the tasks dependencies.

Other tasks are cohort tasks, so they can take a `--samples` parameter (skip
it to run on all present samples):

```
paip JointGenotyping --samples Sample1,Sample2
```

You can use `paip -h` to get a list of the available parameters.

