# GPG & Hardware Tokens

<img src="/assets/Yubikey-Header.jpeg" alt="Header Img" width=100%/>

## TL;DR
 * [Preamble](#Preamble)
 * [Requirements](#Requirements)
   * [Configuration](#Configuration)
 * [Our GPG key structure](#Our GPG key structure)
   * [Creating the Master Cert Key](#Creating the Master Cert Key)
   * [Master Key Revocation](#Master Key Revocation)
   * [Subkey Generation](#Subkey Generation)
   * [Exporting our keys](#Exporting our keys)
     * [Exporting Public Keys](#Exporting Public Keys)
     * [Exporting Private Keys](#Exporting Private Keys)
 * [Writing our Keys to a Yubikey](#Writing our Keys to a Yubikey)
 * [GPG Private Key Cleanup](#GPG Private Key Cleanup)
 * [Publishing our Public GPG keys](#Publishing our Public GPG keys)
 * [Setting our SSH agent use our GPG keys](#Setting our SSH agent use our GPG keys)
   * [Adding our public key to various authorized keys](#Adding our public key to various authorized keys)
 * [Setting touch behavior for Yubikey Subkeys](#Setting touch behavior for Yubikey Subkeys)
 * [Setting pin retries for Yubikey](#Setting pin retries for Yubikey)
 * [Setting pins for your Smart Card](#Setting pins for your Smart Card)

## Preamble

Every time I set up a new computer there is a fair amount of time spent on getting various configs into a state I am comfortable with. Unfortunately, I don't have a means to automatically set up hardware tokens for authing into some machines so I often have to spend a day just looking up all the various commands and parameters. This post aims to make that process easier for me in the future, but also hopefully save you some time on your next gpg key setup.

I also am using the **Yubikey 5** because [it supports the GPG 3.4 Smart Card spec](https://support.yubico.com/support/solutions/articles/15000027139-yubikey-5-2-3-enhancements-to-openpgp-3-4-support). Allowing us to write elliptic curve keypairs to the device. If you have a yubikey 4 or lower you will have to use RSA as your algorithm for all keys in this process.

I don't claim to be a cryptography expert, and what I am posting here is to the best of my knowledge the most generic use case friendly way to set up a hardware token. If you have improvements feel free to send me a pgp message with the details.

## Requirements

We are ensuring we have three programs for the following:

* GPG - for creating and setting keys for smart-cards
* PinEntry - a generic modal that will pop up when we need to enter our smart card's pin
* YkMan - a program that we can use to set the pins on our Yubikey, and require a human to touch it to auth

For MacOS I assume that you are using homebrew or are able to get these programs from valid sources

```b
brew install gnupg pinentry-mac ykman
```

For Linux I am using a Debian based package manager, but I trust you are able to find these packages with your specific distro.

```b
sudo apt install gpg scdaemon libccid pinentry yubikey-manager
```

### Configuration

We need to tell our gpg-agent what our pinentry program is as well as that we plan to use our gpg agent for ssh

for MacOS

```b
echo "pinentry-program /usr/local/bin/pinentry-mac\nenable-ssh-support" > $HOME/.gnupg/gpg-agent.conf
```

for Linux

```b
echo "pinentry-program /usr/bin/pinentry\nenable-ssh-support" > $HOME/.gnupg/gpg-agnet.conf
```

## Our GPG key structure

What we are working towards is a single GPG master key that certifies multiple subkeys for specific actions, namely: *Authorizing*, *Signing*, and *Encrypting*. When we talk about a key in this context, we are referring to a key-pair. Meaning we will be making 8 keys in total 4 private and 4 public.

```b
Master (Certify)
  |
  |--> Sub 1 (Signing)
  |
  |--> Sub 2 (Encrypting)
  |
  \--> Sub 3 (Authorizing)
```

I understand that there are mechanisms to run this as a batch job, however I want to walk through the steps manually first.

### Creating the Master Cert Key

```b
gpg --expert --full-generate-key --cert-digest-algo H10
```

**\*Note\*** The `--cert-digest-algo` flag allows us to specify the hashing algorithm on these keys. By default we will see SHA256, which is fine for most everyone, but since we can specify SHA512 which will be faster on our 64-bit machines, and also make a collision with our hash much less likely. [According to the Docs](https://www.gnupg.org/gph/en/manual/r2029.html) we can show the algorithms used here, but only some of them map to the globals in *gcrypt.h* so no love on specifying whatever hash you want ¯\\_(ツ)_/¯

We select `(11) ECC (set your own capabilites` and we then toggle the signing capability `s` which is on by default so that only the certify capability remains.

![gpg capability selection](/assets/gpg-capability-selection.png)

Finally we select `(Q) Finished` to then specify the encryption algorithm. In our case we want `(1) Curve 25519`

Next we are prompted with how long we want this cert to be valid for. I normally don't like to set limits for how long a key will be used in fear that I will lose historical data. That being said, I also limit the damage that is done if these keys are compromised by creating a revocation certificate. So, I enter a `0` and confirm with `y` to state that my master key will not expire.

Now we want to provide some information about who the key belongs to. I'll enter `shiddy` for my name and `shiddy@shiddy.io` for my email, and leave the comment blank. We then finalize the key creation with `(O)kay`.

At this point you may be prompted for a passphrase, **This is different than your smart card pin**, and is the only thing preventing this key from being used if someone gets access to your keyring or private key storage. Make sure to set it to something secure.

Congrats! We now will follow a similar sequence of steps to generate our *Authorization*, *Encryption*, and *Signing* keys.

If we want to confirm our key status at any time we can execute `gpg --export shiddy@shiddy.io | gpg --list-packets`

Which at this point shows that we have generated two keys `pkey[0]` and `pkey[1]` as well as our `digest algo H10` as part of the signature packet.

![gpg list packets example](/assets/gpg-list-packets-example.png)

### Master Key Revocation

We want to make a means for us to say that this key has been compromised if we make a mistake in the future.

This is important because we set this key to never expire, if our key was compromised we have no means of informing others. That being said, we also need to make sure that this revocation certificate is as secure as our Master secret key, otherwise anyone could revoke our keys.

```b
gpg --output shiddy\@shiddy.io.gpg-revocation-certificate --gen-revoke shiddy@shiddy.io
```

The above command created a file `shiddy@shiddy.io.gpg-revocation-certificate` which contains the revocation certificate, print it and put in in a fire-safe, slap it on a usb and put it somewhere safe but **do not keep it on your hard drive**

### Subkey Generation

We want to create our subkeys from our master Certify key. So we will tell GPG that we want to edit this key which will drop us into a gpg prompt.

```b
gpg --expert --edit-key --cert-digest-algo H10 shiddy@shiddy.io
```

We can then enter `addkey` to begin the creation of a new subkey.

Selecting `(11) ECC (set your own capabilities)` again will default to *Sign* as the only action, but we should confirm this and then Finalize our key selection with `(Q) Finished`, `(1) Curve 25519` for the elliptic curve we want, that it will not expire with `0`, and a confirmation of `y`.

Two more to go! Let's create our *Authenticate* key next

Invoke `addkey` again, `(11) ECC (set your own capabilities)` and this time only enabling the *Authorization* capability and disabling any other capabilities. `0` for the expiration date, and a confirmation with `y`.

One final `addkey`, `(12) ECC (encrypt only)`, `(1) Curve 25519` for the elliptic curve, `0` for the expiration date, and finally `y` to confirm

finally we want to cleanly exit gpg with `save`.

Huzzah! We now have a bunch of public and private keys!

If we note what is returned to us here, we can see our master key set up with `sec ed25519` and our *Sign* and *Authenticate* keys as `ssb ed25519`. However our *Encryption* key is a `ssb cv25519` which specifies that it's going to be using an *integrated encryption scheme* (IES) to encrypt since the plaintext that can be encrypted in most elliptic curves is much smaller than RSA at similar bit lengths.

It's also worth point out that we could create any subkey with any algorithm you desire, so if you for example worked at a place where it might not be guaranteed that you can ssh with elliptic curves, then you can reasonably only create the Authorization key as a RSA4096 while keeping the other two subkey pairs as EC25519.

We can optionally add an image to this key with `addphoto` but it's worth noting that this is going to be stored on other people's machines, and that we don't want to make the people offering free cryptography solutions sad, so limiting the size is ideal.

### Exporting our keys

We are now ready to export our keys.

We will export our secret keys we want to backup, as well as write to our smart card. We will also export our public keys, which we can publish to external hosts.

#### Exporting Public Keys

```b
gpg --export -a shiddy@shiddy.io > shiddy\@shiddy.io.pub
```

#### Exporting Private Keys

```b
gpg --export-secret-keys -a shiddy@shiddy.io > shiddy\@shiddy.io.priv
```

The two export commands we ran created two files `shiddy@shiddy.io.pub` and `shiddy@shiddy.io.priv` we want to save the private file one in the same place as our `shiddy@shiddy.io.gpg-revocation-certificate` from before. Making sure to remove them from the hard drive after doing so.

## Writing our Keys to a Yubikey

Let's check that our computer is able to read the smart card data. After plugging in our card we can run `gpg --card-status` to see what cards are plugged in, as well as what Signing, Encryption, and Authentication keys are on the device.

If you are not starting out fresh, you can always run `ykman piv reset && ykman openpgp reset`

**Note** The `ykman openpgp reset` command resets your pin to 123456 and admin pin to 12345678. It's assumed that you know your pin and admin pin. We will change it to something else later in [Setting pins for your Smart Card](#Setting pins for your Smart Card) below.

**Note** if you find you are getting errors like `Error: Failed connecting to YubiKey ... Make sure the application have require permissions` You might need to unplug and replug in your hardware device. We are making many changed in the course of this post and sometimes it can lock after it's been updated.

```b
gpg --edit-key shiddy@shiddy.io
```

Here we want to select a specific subkey with `key 1` and then telling saying that specific key should be sent to our smart card with `keytocard`.

**Note** You will see that the specific subkey is selected when it has an asterisk **(\*)** next to it

Since our key selected earlier was a signature key we inform the smart card it's a signature key with `(1) Signature Key`

Tada!

We can follow this patter for our *Authentication* and *Encryption* subkeys:

Deselect our signature key with `key 1`, select our Auth key with `key 2`, apply it to the card with `keytocard`, and tell the smart card it's an authentication key with `(2) Authentication Key`.

![gpg keytocard example](/assets/gpg-keytocard-example.png)

Finally writing our Encryption key via: Deselecting our authentication key with `key 2`, selecting our encryption key with `key 3`, writing it to the card with `keytocard`, and telling the card it's an encryption key with `(3) Encryption Key`.

Now we cleanly close gpg with `save`.

## GPG Private Key Cleanup

We will want to remove our private keys from GPG since they are now all written to our smart card

```b
gpg --delete-secret-and-public-keys
```

We will want to import our public keys to our GPG suite since it will be able to map them to the private keys on our smart card.

```b
gpg --import shiddy\@shiddy.io.pub
```

The state of our system can be confirmed by running `gpg --card-status | tail` and seeing whether the output is similar to the following:

```b
sec#  ed25519 ...
ssb>  ed25519 ...
ssb>  ed25519 ...
ssb>  cv25519 ...
```

What this tells us is that GPG has mapped some of the public keys we imported to private keys on this card. The **sec#** and **ssb>** inform us that gpg knows of a key but it does not have direct access to it.

If we want to see public keys in our keyring we can type `gpg -k` which should show

```b
pub  ed25519 ... [C]
sub  ed25519 ... [S]
sub  ed25519 ... [A]
sub  cv25519 ... [E]
```

Conversely if we want to see private keys we can type `gpg -K` which should show output similar to the end of `gpg --card-status`

## Publishing our Public GPG keys

Since we have public keys that others have to trust, we have to publish them on places that are tied to our identity. Commonly this is done with various keyservers:

http://keyserver.ubuntu.com/#
http://pgp.mit.edu/
https://keyserver.pgp.com/vkd/GetWelcomeScreen.event


## Setting our SSH agent use our GPG keys

I place a path variable in my .bash_profile, however if you use another shell you might want to add it to it's appropriate profile/runcommand config.

```b
echo "\nexport SSH_AUTH_SOCK=\"$(gpgconf --list-dirs agent-ssh-socket)\"" >> ~/.bash_profile
```

remember to source your new config as well `source ~/.bash_profile`

### Adding our public key to various authorized keys

We can print our public authentication key with the following:

```b
ssh-add -L
```

Which can then be added to any of the expected authorized_keys files.

## Setting touch behavior for Yubikey Subkeys

Here we are setting the state of the touch behavior for all our subkeys on our smart card. We have a few states to choose from.
If you would like to read more about them you can read them with `ykman openpgp set-touch -h`.

Unless you are doing any scripting where you would need to ssh to a bunch of places over some reasonable period of time, set your policy to `Cached` instead of `On`, and if you don't want anyone to change this policy on your smart card, you can set `fixed` or `cached-fixed` so that it can't be changed apart from a factory reset of the yubikey.

```b
POLICY="On"
ykman openpgp set-touch $POLICY SIG
ykman openpgp set-touch $POLICY AUT
ykman openpgp set-touch $POLICY ENC
```

## Setting pin retries for Yubikey

We have some extra protections with our Yubikey that are worth enabling. Yubikey will lock out a key if a user fails to enter the correct password a number of times. However if you are like me and use a keyboard without any labels, you might want to make these thresholds more lenient.

Here I am setting the number of retries for my pin to 5, the number of reset-code retries to 5 and the number of admin-pin retries to 10

```b
ykman openpgp set-pin-retiries 5 5 10
```

## Setting pins for your Smart Card

Smart Cards generally have two pins, a pin for regular verification of the card owner, and an admin pin for making hardware changes to the smart card itself.

If we fail validation with the pin a number of time above our pin retry count, we have to use the administrative pin to unlock the key. If we fail to validate the admin key in the same way, we brick our key, and would have to factory reset it.

We can change these pins as well as unblock our pin with gpg, using the following command:

```b
gpg --change-pin
```

*If you have not modified this value yet, 123456 is the factory pin and 12345678 is the default administrative pin*

<p id="date">written on 2020-09-07</p>
